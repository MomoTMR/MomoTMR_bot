"""
Обработчик системы квизов.

Этот модуль реализует conversation handler для проведения квизов по различным темам.
Поддерживает:
- Выбор темы квиза из предустановленного списка
- Генерацию вопросов через ChatGPT для каждой темы
- Проверку ответов пользователя
- Ведение статистики правильных/неправильных ответов
- Возможность смены темы или продолжения квиза

Состояния conversation handler:
- SELECTING_TOPIC: выбор темы для квиза
- ANSWERING_QUESTION: ответ на вопросы квиза
"""

import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers import basic
from services.openai_client import get_personality_response
from data.quiz_topics import get_quiz_topics_keyboard, get_quiz_topic_data, get_quiz_continue_keyboard

logger = logging.getLogger(__name__)

SELECTING_TOPIC, ANSWERING_QUESTION = range(2)


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /quiz - запуск системы квизов.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения
    """
    logger.info('Обрабатываю нажатие на /quiz')
    await quiz_start(update, context)


async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет меню выбора темы квиза.

    Отправляет изображение с описанием доступных тем квиза и inline клавиатурой
    для выбора темы.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: SELECTING_TOPIC для перехода в состояние выбора темы
    """
    try:
        image_path = "data/images/quiz.png"
        logger.info(f'В квизе используется картинка: {image_path}')
        message_text = (
            "🧠 <b>Квиз - проверь свои знания!</b>\n\n"
            "Выберите тему для квиза:\n\n"
            "💻 <b>Программирование</b> - вопросы о коде и технологиях\n"
            "🏛️ <b>История</b> - исторические факты и события\n"
            "🔬 <b>Наука</b> - физика, химия, биология\n"
            "🌍 <b>География</b> - страны, столицы, природа\n"
            "🎬 <b>Кино</b> - фильмы, актеры, режиссеры\n\n"
            "Каждый вопрос имеет 4 варианта ответа!"
        )

        keyboard = get_quiz_topics_keyboard()

        if update.message:
            await update.message.delete()

            if os.path.exists(image_path):
                try:
                    await update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения в квизе: {e}")
                    await update.message.reply_text(
                        text=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
            else:
                await update.message.reply_text(
                    text=message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )

        elif update.callback_query:
            query = update.callback_query
            await query.answer()

            if os.path.exists(image_path):
                try:
                    await query.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                    await query.message.delete()
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения через callback в квизе: {e}")
                    await query.edit_message_text(
                        text=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
            else:
                await query.edit_message_text(
                    text=message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )

        return SELECTING_TOPIC

    except Exception as e:
        logger.error(f"Ошибка в quiz_start: {e}", exc_info=True)
        return SELECTING_TOPIC


async def topic_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик выбора темы квиза.

    Сохраняет выбранную тему, инициализирует счетчики и генерирует первый вопрос.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: ANSWERING_QUESTION для перехода в состояние ответа на вопросы
    """
    query = update.callback_query
    await query.answer()

    try:
        # Извлекаем тему из callback_data
        topic_key = query.data.replace("quiz_topic_", "")
        topic_data = get_quiz_topic_data(topic_key)

        if not topic_data:
            await query.edit_message_text("❌ Ошибка: тема не найдена")
            return SELECTING_TOPIC

        # Сохраняем данные в контексте
        context.user_data['quiz_topic'] = topic_key
        context.user_data['topic_data'] = topic_data
        context.user_data['correct_answers'] = 0
        context.user_data['total_questions'] = 0

        logger.info(f"Выбрана тема квиза: {topic_key}")

        # Генерируем первый вопрос
        await generate_question(update, context)

        return ANSWERING_QUESTION

    except Exception as e:
        logger.error(f"Ошибка в topic_selected: {e}", exc_info=True)
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте снова.")
        return SELECTING_TOPIC


async def generate_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Генерирует новый вопрос для текущей темы квиза.

    Использует ChatGPT для создания вопроса с 4 вариантами ответа
    на основе промпта выбранной темы.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст с данными темы
    """
    try:
        topic_data = context.user_data.get('topic_data')
        if not topic_data:
            await update.callback_query.edit_message_text("❌ Ошибка: тема не найдена")
            return

        # Показываем индикатор загрузки
        await update.callback_query.edit_message_text("🤔 Генерирую вопрос... ⏳")

        # Генерируем вопрос через ChatGPT
        question_response = await get_personality_response("Создай новый вопрос", topic_data['prompt'])

        # Парсим ответ
        parsed_question = parse_question_response(question_response)

        if not parsed_question:
            await update.callback_query.edit_message_text(
                "❌ Ошибка генерации вопроса. Попробуйте еще раз.",
                reply_markup=get_quiz_continue_keyboard(context.user_data['quiz_topic'])
            )
            return

        # Сохраняем правильный ответ
        context.user_data['correct_answer'] = parsed_question['correct_answer']
        context.user_data['total_questions'] += 1

        # Формируем сообщение с вопросом
        question_text = (
            f"📝 <b>Вопрос #{context.user_data['total_questions']}</b>\n\n"
            f"{parsed_question['question']}\n\n"
            f"A) {parsed_question['option_a']}\n"
            f"B) {parsed_question['option_b']}\n"
            f"C) {parsed_question['option_c']}\n"
            f"D) {parsed_question['option_d']}\n\n"
            f"<i>Напишите букву правильного ответа (A, B, C или D)</i>"
        )

        await update.callback_query.edit_message_text(
            question_text,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Ошибка в generate_question: {e}", exc_info=True)
        await update.callback_query.edit_message_text(
            "❌ Произошла ошибка при генерации вопроса.",
            reply_markup=get_quiz_continue_keyboard(context.user_data.get('quiz_topic', ''))
        )


def parse_question_response(response_text):
    """
    Парсит ответ ChatGPT и извлекает компоненты вопроса.

    Args:
        response_text (str): Ответ от ChatGPT с вопросом

    Returns:
        dict: Словарь с компонентами вопроса или None при ошибке парсинга
    """
    try:
        lines = response_text.strip().split('\n')
        question = ""
        options = {}
        correct_answer = ""

        for line in lines:
            line = line.strip()
            if line.startswith("Вопрос:"):
                question = line.replace("Вопрос:", "").strip()
            elif line.startswith("A)"):
                options['option_a'] = line.replace("A)", "").strip()
            elif line.startswith("B)"):
                options['option_b'] = line.replace("B)", "").strip()
            elif line.startswith("C)"):
                options['option_c'] = line.replace("C)", "").strip()
            elif line.startswith("D)"):
                options['option_d'] = line.replace("D)", "").strip()
            elif "Правильный ответ:" in line:
                correct_answer = line.split(":")[-1].strip().upper()

        if question and len(options) > 2: # and correct_answer in ['A', 'B', 'C', 'D']:
            return {
                'question': question,
                'correct_answer': correct_answer,
                **options
            }
        else:
            logger.warning(f"Не удалось распарсить вопрос: {response_text}")
            return None

    except Exception as e:
        logger.error(f"Ошибка парсинга вопроса: {e}")
        return None


async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик ответа пользователя на вопрос квиза.

    Проверяет правильность ответа, обновляет статистику и предлагает
    продолжить квиз или сменить тему.

    Args:
        update (Update): Объект обновления от Telegram с ответом пользователя
        context (ContextTypes.DEFAULT_TYPE): Контекст с данными квиза

    Returns:
        int: ANSWERING_QUESTION для продолжения квиза
    """
    try:
        user_answer = update.message.text.strip().upper()
        correct_answer = context.user_data.get('correct_answer')

        if user_answer not in ['A', 'B', 'C', 'D']:
            await update.message.reply_text(
                "❓ Пожалуйста, ответьте буквой A, B, C или D"
            )
            return ANSWERING_QUESTION

        # Проверяем ответ
        is_correct = user_answer == correct_answer
        if is_correct:
            context.user_data['correct_answers'] += 1

        # Формируем ответ
        correct_count = context.user_data.get('correct_answers', 0)
        total_count = context.user_data.get('total_questions', 0)

        if is_correct:
            result_text = f"✅ <b>Правильно!</b>"
        else:
            result_text = f"❌ <b>Неправильно!</b> Правильный ответ: {correct_answer}"

        stats_text = f"\n\n📊 <b>Статистика:</b> {correct_count}/{total_count} правильных ответов"

        # Удаляем сообщение пользователя
        await update.message.delete()

        # Отправляем результат с меню
        await update.message.reply_text(
            result_text + stats_text,
            parse_mode='HTML',
            reply_markup=get_quiz_continue_keyboard(context.user_data['quiz_topic'])
        )

        return ANSWERING_QUESTION

    except Exception as e:
        logger.error(f"Ошибка в handle_quiz_answer: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка при обработке ответа.")
        return ANSWERING_QUESTION


async def handle_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик callback query для управления квизом.

    Обрабатывает кнопки:
    - "Ещё вопрос" - генерирует новый вопрос по той же теме
    - "Сменить тему" - возвращает к выбору темы
    - "Закончить квиз" - завершает квиз и возвращает в главное меню

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: Соответствующее состояние в зависимости от выбранного действия
    """
    query = update.callback_query
    await query.answer()

    if query.data.startswith("quiz_continue_"):
        # Генерируем новый вопрос
        await generate_question(update, context)
        return ANSWERING_QUESTION

    elif query.data == "quiz_change_topic":
        # Смена темы
        return await quiz_start(update, context)

    elif query.data == "quiz_finish":
        # Завершение квиза
        correct_count = context.user_data.get('correct_answers', 0)
        total_count = context.user_data.get('total_questions', 0)

        final_text = (
            f"🏁 <b>Квиз завершен!</b>\n\n"
            f"📊 <b>Итоговая статистика:</b>\n"
            f"Правильных ответов: {correct_count}/{total_count}\n"
        )

        if total_count > 0:
            percentage = (correct_count / total_count) * 100
            final_text += f"Процент правильных ответов: {percentage:.1f}%\n\n"

            if percentage >= 80:
                final_text += "🎉 Отличный результат!"
            elif percentage >= 60:
                final_text += "👍 Хороший результат!"
            elif percentage >= 40:
                final_text += "👌 Неплохо, но можно лучше!"
            else:
                final_text += "📚 Стоит подучиться!"

        await query.edit_message_text(final_text, parse_mode='HTML')

        context.user_data.clear()
        await asyncio.sleep(3)
        await basic.start(update, context)
        return -1

    return ANSWERING_QUESTION
