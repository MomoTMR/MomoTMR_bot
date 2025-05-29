"""Файл с хендлерами бота."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio
# from handlers import random_fact


logger = logging.getLogger(__name__)

# Срабатывает каждый раз когда бот получает команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, reply_markup=None):
    logger.info("Start mode")

    """Обработка команды /start."""
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомный факт", callback_data="random_fact")],
        [InlineKeyboardButton("🤖 ChatGPT (скоро)", callback_data="gpt_coming_soon")],
        [InlineKeyboardButton("👥 Диалог с личностью (скоро)", callback_data="talk_coming_soon")],
        [InlineKeyboardButton("🧠 Квиз (скоро)", callback_data="quiz_coming_soon")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🎉 <b>Добро пожаловать в ChatGPT бота!</b>\n\n"
        "🚀 <b>Доступные функции:</b>\n"
        "• Рандомный факт - получи интересный факт\n"
        "• ChatGPT - общение с ИИ (в разработке)\n"
        "• Диалог с личностью - говори с известными людьми (в разработке)\n"
        "• Квиз - проверь свои знания (в разработке)\n\n"
        "Выберите функцию из меню ниже:"
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок главного меню"""
    logger.info("Обработка нажатий")
    query = update.callback_query
    await query.answer()

        await query.edit_message_text(
            "🚧 <b>Функция в разработке!</b>\n\n"
            "Эта функция будет добавлена на следующих уроках.\n"
            "Пока что попробуйте 'Рандомный факт'!",
            parse_mode='HTML'
        )

        await asyncio.sleep(3)
        await start_menu_again(query)

async def start_menu_again(query):
    """Возврат в главное меню"""
    logger.info("Старт меню again")
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомный факт", callback_data="random_fact")],
        [InlineKeyboardButton("🤖 ChatGPT (скоро)", callback_data="gpt_coming_soon")],
        [InlineKeyboardButton("👥 Диалог с личностью (скоро)", callback_data="talk_coming_soon")],
        [InlineKeyboardButton("🧠 Квиз (скоро)", callback_data="quiz_coming_soon")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🎉 <b>Добро пожаловать в ChatGPT бота!</b>\n\n"
        "Выберите одну из доступных функций:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )