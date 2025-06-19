"""
Обработчик для диалога с различными личностями.

Этот модуль реализует conversation handler для диалога пользователя с различными
личностями через ChatGPT. Поддерживает:
- Выбор из предустановленных личностей
- Персонифицированные ответы через OpenAI API
- Управление состоянием диалога
- Интерактивное меню с изображениями

Состояния conversation handler:
- SELECTION_PERSONALITY: выбор личности для диалога
- CHATING_WITH_PERSONALITY: активный диалог с выбранной личностью
"""

import logging
from statistics import quantiles

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, ConversationHandler
import os

from data.personalities import get_personality_data, get_personality_keyboard
from handlers import basic
from services.openai_client import get_personality_response

logger = logging.getLogger(__name__)

SELECTION_PERSONALITY, CHATING_WITH_PERSONALITY = range(2)

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /talk - запуск диалога с личностью.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения
    """
    logging.info(f"Обработка команды /talk")
    await talk_start(update, context)

async def talk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет меню выбора личностей для диалога.

    Отправляет изображение с описанием функции и inline клавиатурой
    для выбора доступных личностей.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: SELECTION_PERSONALITY для перехода в состояние выбора личности
    """
    logging.info(f"Обработка кнопки talk_interface")
    try:
        image_path = "data/images/personality.png"
        message_text = (
            "Диалог с известной личностью\n\n"
            "Выберете с кем хотите общаться\n\n"
            "Выберите личность:"
        )

        keyboard = get_personality_keyboard()

        if update.message:
            logging.info("Обработка команды /talk")
            await update.message.delete()

            if os.path.exists(image_path):
                try:
                    await update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=message_text,
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logging.error(f"Ошибка отправки изображения: {e}")
                    await update.message.reply_text(
                        text=message_text,
                        reply_markup=keyboard
                    )
            else:
                await update.message.reply_text(
                    text=message_text,
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
                        reply_markup=keyboard
                    )
                    await query.message.delete()
                except Exception as e:
                    logging.error(f"Ошибка отправки изображения через callback: {e}")
                    await query.edit_message_text(
                        text=message_text,
                        reply_markup=keyboard
                    )
            else:
                await query.edit_message_text(
                    text=message_text,
                    reply_markup=keyboard
                )

        return SELECTION_PERSONALITY

    except Exception as e:
        logging.error(f"Ошибка в talk_start: {e}", exc_info=True)
        return SELECTION_PERSONALITY

async def personality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик выбора личности для диалога.

    Сохраняет выбранную личность в контексте пользователя и отправляет
    приветственное сообщение от выбранной личности.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: CHATING_WITH_PERSONALITY для перехода в состояние диалога
    """
    logging.info(f"Обработка выбора личности")
    query = update.callback_query
    await query.answer()

    try:
        logging.info(f"Извлекаем ключ личности из callback_data")
        personality_key = query.data.replace("personality_", "")
        personality = get_personality_data(personality_key)
        logging.info(f"Проверка переменной {personality}")
        if not personality:
            await query.edit_message_text("Ошибка: личность не найдена")
            return SELECTION_PERSONALITY

        # Сохраняем данные личности в контексте
        context.user_data['current_personality'] = personality_key
        context.user_data['personality_data'] = personality

        # Создаем меню для диалога
        keyboard = [
            # [InlineKeyboardButton("✉️ Продолжить диалог", callback_data="continue_chat")],
            [InlineKeyboardButton("🔄 Сменить личность", callback_data="change_personality")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="finish_talk")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🎭 Выбрана личность: {personality['emoji']} {personality['name']}\n\n"
            f"Теперь напишите любое сообщение, и я отвечу от лица этой личности!",
            reply_markup=reply_markup
        )

        return CHATING_WITH_PERSONALITY

    except Exception as e:
        logging.error(f"Ошибка в personality_selected: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка. Попробуйте снова.")
        return SELECTION_PERSONALITY

async def handle_personality_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовых сообщений для диалога с личностью.

    Получает сообщение пользователя, отправляет его в ChatGPT с промптом
    выбранной личности и возвращает персонифицированный ответ.

    Args:
        update (Update): Объект обновления от Telegram с текстовым сообщением
        context (ContextTypes.DEFAULT_TYPE): Контекст с данными личности

    Returns:
        int: CHATING_WITH_PERSONALITY для продолжения диалога
    """
    logger.info(f"Получено сообщение в Personality: {update.message.text}")
    try:
        user_message = update.message.text
        personality_key = context.user_data.get('current_personality')
        personality_data = context.user_data.get('personality_data')

        if not personality_key or not personality_data:
            await update.message.reply_text(
                f"Произошла ошибка: личность не выбрана. Используйте /talk для начала {personality_key} {personality_data}"
            )
            return CHATING_WITH_PERSONALITY

        # Показываем индикатор печати
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Отправляем сообщение о обработке
        processing_msg = await update.message.reply_text("🤔 Обрабатываю ваш запрос... ⏳")

        # Получаем ответ от личности
        response = await get_personality_response(user_message, personality_data['prompt'])

        # Создаем меню для продолжения
        keyboard = [
            # [InlineKeyboardButton("✉️ Продолжить диалог", callback_data="continue_chat")],
            [InlineKeyboardButton("🔄 Сменить личность", callback_data="change_personality")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="finish_talk")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Удаляем сообщение о обработке
        await processing_msg.delete()
        # Отправляем ответ
        await update.message.reply_text(
            f"{personality_data['emoji']} <b>{personality_data['name']} отвечает:</b>\n\n{response}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        return CHATING_WITH_PERSONALITY

    except Exception as e:
        logger.error(f"Ошибка в handle_personality_message: {e}", exc_info=True)
        await update.message.reply_text("😔 Произошла ошибка при получении ответа. Попробуйте снова.")
        return CHATING_WITH_PERSONALITY

async def handle_personality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик callback query для управления диалогом с личностью.

    Обрабатывает кнопки:
    - "Продолжить диалог" - остается в том же состоянии
    - "Сменить личность" - возвращает к выбору личности
    - "Вернуться в меню" - завершает диалог

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: Соответствующее состояние в зависимости от выбранного действия
    """
    query = update.callback_query
    logger.info(f"Получен callback в Personality: {query.data}")
    await query.answer()

    if query.data == "continue_chat":
        personality_data = context.user_data.get("personality_data")
        if personality_data:
            pass  # Заглушка на перезапуск диалога.
            logger.info("Здесь продолжение диалога с той же личностью")
        return CHATING_WITH_PERSONALITY

    elif query.data == "change_personality":
        logger.info("Смена личности")
        return await talk_start(update, context)

    elif query.data == "finish_talk":
        logger.info("Завершение диалога с личностью")
        context.user_data.clear()
        await basic.start(update, context)
        return ConversationHandler.END

    return CHATING_WITH_PERSONALITY
