import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.openai_client import get_random_fact
from handlers import basic

logger = logging.getLogger(__name__)


async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /random_fact"""
    logger.info("Запуск обработки random_fact")
    try:
        loading_msg = await update.message.reply_text("🎲 Генерирую интересный факт... ⏳")
        fact = await get_random_fact()
        keyboard = [
                    [InlineKeyboardButton("🎲 Хочу ещё факт", callback_data="random_more")],
                    [InlineKeyboardButton("🏠 Закончить", callback_data="random_finish")]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await loading_msg.edit_text(
            f"🧠 <b>Интересный факт:</b>\n\n{fact}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при получении факта от OpenAI: {e}")
        await update.message.reply_text("🤔 К сожалению, не удалось получить факт в данный момент. Попробуйте позже!")


async def random_fact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок для рандомных фактов"""
    logger.info("Обработка нажатий кнопок для рандомных фактов")
    query = update.callback_query
    await query.answer()

    if query.data == "random_more":
        logger.info("Обработка random_more")
        try:
            await query.edit_message_text("🎲 Генерирую новый факт... ⏳")

            fact = await get_random_fact()
            keyboard = [
                [InlineKeyboardButton("🎲 Хочу ещё факт", callback_data="random_more")],
                [InlineKeyboardButton("🏠 Закончить", callback_data="random_finish")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

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
        await basic.start_menu_again(query)

    elif query.data == "random_fact":
        logger.info("Обработка random_fact")
        try:
            await query.edit_message_text("🎲 Генерирую интересный факт... ⏳")

            fact = await get_random_fact()
            keyboard = [
                [InlineKeyboardButton("🎲 Хочу ещё факт", callback_data="random_more")],
                [InlineKeyboardButton("🏠 Закончить", callback_data="random_finish")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"🧠 <b>Интересный факт:</b>\n\n{fact}",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Ошибка при получении факта из меню: {e}")
            await query.edit_message_text(
                "😔 Произошла ошибка. Попробуйте позже.\n"
                "Используйте /start чтобы вернуться в меню."
            )