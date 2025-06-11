"""Файл с хендлерами бота."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio
from handlers import chatgpt_interface

logger = logging.getLogger(__name__)




# Срабатывает каждый раз когда бот получает команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, reply_markup=None):
    logger.info("Команда /start вызвана или fallback")

    welcome_text = (
        "🎉 <b>Добро пожаловать в ChatGPT бота!</b>\n\n"
        "🚀 <b>Доступные функции:</b>\n"
        "• Рандомный факт - получи интересный факт\n"
        "• ChatGPT - общение с ИИ\n"
        "• Диалог с личностью - говори с известными людьми\n"
        "• Квиз - проверь свои знания\n"
        "• Переводчик\n\n"
        "Выберите функцию из меню ниже:"
    )
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомный факт", callback_data="random_fact")],
        [InlineKeyboardButton("🤖 ChatGPT", callback_data="gpt_interface")],
        [InlineKeyboardButton("👥 Диалог с личностью", callback_data="talk_interface")],
        [InlineKeyboardButton("🧠 Поиграем в Квиз ?", callback_data="quiz_interface")],
        [InlineKeyboardButton("🥸 Переводчик на разные языки", callback_data="translate_interface")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        if update.message:  # Вызов через команду или сообщение
            await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
        elif update.callback_query:  # Вызов через callback
            query = update.callback_query
            await query.message.delete()  # Удаляем сообщение с кнопкой
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=welcome_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            await query.answer()
        return -1
    except Exception as e:
        logger.error(f"Ошибка в start: {e}", exc_info=True)
        return -1

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок главного меню"""
    query = update.callback_query
    logger.info(f"Получен Callback в basic: {query.data}")
    logger.info(f"Текущее состояние: {context.user_data.get('state')}")

    await query.answer()

    if query.data in ["quiz_coming_soon"]:
        await query.edit_message_text(
            "🚧 <b>Функция в разработке!</b>\n\n"
            "Эта функция будет добавлена на следующих уроках.\n"
            "Пока что попробуйте 'Рандомный факт'!",
            parse_mode='HTML'
        )

        await asyncio.sleep(3)
        await start(update,context)