"""
Обработчик для генерации случайных фактов.

Этот модуль содержит функции для обработки команды получения случайных фактов
с использованием OpenAI API. Поддерживает как прямой вызов команды /random,
так и интерактивные кнопки для получения дополнительных фактов.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.openai_client import get_random_fact
from handlers import basic

logger = logging.getLogger(__name__)

keyboard = [
    [InlineKeyboardButton("🎲 Хочу ещё факт", callback_data="random_more")],
    [InlineKeyboardButton("🏠 Закончить", callback_data="random_finish")]
]

reply_markup = InlineKeyboardMarkup(keyboard)

async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /random для получения случайного факта.

    Генерирует случайный факт с помощью OpenAI API и отправляет его пользователю
    вместе с inline клавиатурой для получения дополнительных фактов.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды
    """
    logger.info("Запуск обработки random_fact")
    try:
        loading_msg = await update.message.reply_text("🎲 Генерирую интересный факт... ⏳")
        fact = await get_random_fact()
        await loading_msg.edit_text(
            f"🧠 <b>Интересный факт:</b>\n\n{fact}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при получении факта от OpenAI: {e}")
        await update.message.reply_text("🤔 К сожалению, не удалось получить факт в данный момент. Попробуйте позже!")


async def random_fact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик callback query для кнопок рандомных фактов.

    Обрабатывает нажатия кнопок:
    - "Хочу ещё факт" - генерирует новый факт
    - "Закончить" - возвращает в главное меню

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения callback
    """
    query = update.callback_query
    logger.info(f"Обработка нажатий кнопок для рандомных фактов {query.data}")

    await query.answer()

    if query.data in["random_more","random_fact"]:
        logger.info("Обработка random_more")
        try:
            await query.edit_message_text("🎲 Генерирую новый факт... ⏳")
            fact = await get_random_fact()
            await query.edit_message_text(
                f"🧠 <b>Интересный факт:</b>\n\n{fact}",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Ошибка при получении нового факта: {e}")
            await query.edit_message_text(
                "😔 Произошла ошибка. Попробуйте позже.\n"
                "Используйте /start чтобы вернуться в меню."
            )

    elif query.data == "random_finish":
        logger.info("Обработка random_finish")
        await basic.start(update,context)
