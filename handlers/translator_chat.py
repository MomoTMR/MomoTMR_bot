"""
Обработчик переводчика на различные языки.

Этот модуль реализует conversation handler для перевода текста на различные языки
с помощью ChatGPT. Поддерживает:
- Выбор языка для перевода из предустановленного списка
- Двусторонний перевод (русский -> выбранный язык и обратно)
- Сохранение выбранного языка в рамках сессии
- Интерактивное меню с изображениями

Состояния conversation handler:
- SELECTION_LANGUAGE: выбор языка для перевода
- CHATING_WITH_TRANSLATOR: активный режим перевода
"""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, ConversationHandler
import os

from data.languages import get_languages_data, get_translate_keyboard
from handlers import basic
from services.openai_client import get_personality_response

logger = logging.getLogger(__name__)

SELECTION_LANGUAGE, CHATING_WITH_TRANSLATOR = range(2)

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /translate - запуск переводчика.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения
    """
    await translate_start(update, context)

async def translate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет меню выбора языка для перевода.

    Отправляет изображение с описанием функции переводчика и inline клавиатурой
    для выбора доступных языков.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: SELECTION_LANGUAGE для перехода в состояние выбора языка
    """
    try:
        image_path = "data/images/translate.png"
        message_text = (
            "🌍 <b>Переводчик</b>\n\n"
            "Выберите язык для перевода:\n\n"
            "Я могу переводить с русского на выбранный язык и обратно!"
        )

        keyboard = get_translate_keyboard()

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
                    logger.error(f"Ошибка отправки изображения в переводчике: {e}")
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
                    logger.error(f"Ошибка отправки изображения через callback в переводчике: {e}")
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

        return SELECTION_LANGUAGE

    except Exception as e:
        logger.error(f"Ошибка в translate_start: {e}", exc_info=True)
        return SELECTION_LANGUAGE

async def languages_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик выбора языка для перевода.

    Сохраняет выбранный язык в контексте пользователя и отправляет
    приветственное сообщение с инструкциями по использованию переводчика.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: CHATING_WITH_TRANSLATOR для перехода в состояние перевода
    """
    query = update.callback_query
    await query.answer()

    try:
        language_key = query.data.replace("languages_", "")
        language = get_languages_data(language_key)

        if not language:
            await query.edit_message_text("❌ Ошибка: язык не найден")
            return SELECTION_LANGUAGE

        context.user_data['current_language'] = language_key
        context.user_data['language_data'] = language

        keyboard = [
            [InlineKeyboardButton("📝 Продолжить перевод", callback_data="continue_translate")],
            [InlineKeyboardButton("🔄 Сменить язык", callback_data="change_languages")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="finish_translate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"{language['emoji']} <b>Выбран язык: {language['name']}</b>\n\n"
            f"📝 Теперь напишите любой текст, и я переведу его!\n\n"
            f"💡 <b>Примеры:</b>\n"
            f"• Привет, как дела?\n"
            f"• Hello, how are you?\n"
            f"• Что такое искусственный интеллект?\n\n"
            f"Я автоматически определю направление перевода!",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        return CHATING_WITH_TRANSLATOR

    except Exception as e:
        logger.error(f"Ошибка в languages_selected: {e}", exc_info=True)
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте снова.")
        return SELECTION_LANGUAGE

async def handle_languages_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовых сообщений для перевода.

    Получает сообщение пользователя, отправляет его в ChatGPT с промптом
    выбранного языка и возвращает перевод.

    Args:
        update (Update): Объект обновления от Telegram с текстовым сообщением
        context (ContextTypes.DEFAULT_TYPE): Контекст с данными языка

    Returns:
        int: CHATING_WITH_TRANSLATOR для продолжения режима перевода
    """
    logger.info(f"Получено сообщение для перевода: {update.message.text}")
    try:
        user_message = update.message.text
        language_key = context.user_data.get('current_language')
        language_data = context.user_data.get('language_data')

        if not language_key or not language_data:
            await update.message.reply_text(
                "❌ Произошла ошибка: язык не выбран. Используйте /translate для начала"
            )
            return CHATING_WITH_TRANSLATOR
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        processing_msg = await update.message.reply_text("🔄 Перевожу текст... ⏳")
        translation = await get_personality_response(user_message, language_data['prompt'])
        await processing_msg.delete()
        keyboard = [
            [InlineKeyboardButton("🔄 Сменить язык", callback_data="change_languages")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="finish_translate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"{language_data['emoji']} <b>Перевод:</b>\n\n{translation}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return CHATING_WITH_TRANSLATOR

    except Exception as e:
        logger.error(f"Ошибка в handle_languages_message: {e}", exc_info=True)
        await update.message.reply_text("😔 Произошла ошибка при переводе. Попробуйте снова.")
        return CHATING_WITH_TRANSLATOR

async def handle_languages_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик callback query для управления переводчиком.

    Обрабатывает кнопки:
    - "Продолжить перевод" - остается в том же состоянии
    - "Сменить язык" - возвращает к выбору языка
    - "Вернуться в меню" - завершает работу переводчика

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: Соответствующее состояние в зависимости от выбранного действия
    """
    query = update.callback_query
    logger.info(f"Получен callback в Translator: {query.data}")
    await query.answer()

    if query.data == "continue_translate":
        language_data = context.user_data.get("language_data")
        if language_data:
            logger.info("Продолжение перевода с тем же языком")
        return CHATING_WITH_TRANSLATOR

    elif query.data == "change_languages":
        logger.info("Смена языка")
        return await translate_start(update, context)

    elif query.data == "finish_translate":
        logger.info("Завершение работы переводчика")
        context.user_data.clear()
        await basic.start(update, context)
        return ConversationHandler.END

    return CHATING_WITH_TRANSLATOR
