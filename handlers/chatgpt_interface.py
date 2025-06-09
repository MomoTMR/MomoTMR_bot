import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from handlers import basic
from services.openai_client import get_chatgpt_response
import os

logger = logging.getLogger(__name__)


WAITING_FOR_MESSAGE = 1
# Задаем кнопки для inline keyboard.
keyboard = [
    [InlineKeyboardButton("💬 Продолжить этот диалог с OpenAI", callback_data="gpt_continue")],
    [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="gpt_finish")]
]

# Кдадем клаиши в переменную reply_markup
reply_markup = InlineKeyboardMarkup(keyboard)

# Формируем заголовок
CAPTION = (
    "🤖 <b>ChatGPT Интерфейс</b>\n\n"
    "Напишите любой вопрос или сообщение, и я передам его ChatGPT!\n\n"
    "💡 <b>Примеры вопросов:</b>\n"
    "• Объясни квантовую физику простыми словами\n"
    "• Напиши короткий рассказ про кота\n"
    "• Как приготовить пасту карбонара?\n"
    "• Переведи фразу на английский\n\n"
    "✍️ Просто напишите ваш вопрос следующим сообщением:"
)


async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("▶️ Запуск ChatGPT-интерфейса")
    await send_gpt_menu(update, context)
    return WAITING_FOR_MESSAGE

async def continue_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("▶️ Переапуск ChatGPT-интерфейса")
    # await finish_gpt(update,context)
    # await send_gpt_menu(update,context)
    logger.info("Пользователь хочет обнулить чат !!!")
    return WAITING_FOR_MESSAGE

async def send_gpt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_path = "data/images/chatgpt.png"
    caption = CAPTION

    # Удаляем всё лишнее
    if update.message:
        await update.message.delete()

    # await delete_previous_menu(update, context)

    if update.callback_query:
        query = update.callback_query
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                sent = await query.message.edit_media(
                    media=InputMediaPhoto(media=photo, caption=caption, parse_mode='HTML'),
                )
        else:
            sent = await query.message.edit_text(
                text=CAPTION,
                parse_mode='HTML',
            )
        await query.answer()
    else:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                sent = await update.message.reply_photo(
                    photo=photo,
                    caption=CAPTION,
                    parse_mode='HTML',
                )
        else:
            sent = await update.message.reply_text(
                CAPTION,
                parse_mode='HTML',
            )

    # Сохраняем ID, чтобы удалить позже
    context.user_data['gpt_message_id'] = sent.message_id


async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        await delete_previous_menu(update, context)
        user_message = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Отправляем "обрабатываю"
        processing_msg = await update.message.reply_text("🤔 Обрабатываю ваш запрос... ⏳")

        # Получаем ответ от GPT
        gpt_response = await get_chatgpt_response(user_message)

        logger.info(f"Получен ответ от ChatGPT: {gpt_response}")

        # Удаляем сообщение пользователя
        await update.message.delete()

        # Удаляем сообщение о обработке OpenAi
        await processing_msg.delete()


        # Отправляем новый ответ
        response_msg = await update.message.reply_text(
            f"🤖 <b>ChatGPT отвечает:</b>\n\n{gpt_response}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        # Сохраняем новый `message_id` — можно опять использовать для удаления
        context.user_data['gpt_message_id'] = response_msg.message_id

        return WAITING_FOR_MESSAGE

    except Exception as e:
        logger.error(f"💥 Ошибка в GPT обработке: {e}", exc_info=True)
        await update.message.reply_text("😔 Что-то пошло не так. Попробуйте ещё раз.")
        return -1

async def delete_previous_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_id = context.user_data.get('gpt_message_id')
    if message_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
        except Exception as e:
            logger.warning(f"❗ Не удалось удалить меню: {e}")


async def finish_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE,query = None) -> int:
    query = update.callback_query
    await query.answer()

    # Удалим сохранённые данные (если надо)
    context.user_data.clear()

    # await basic.start_menu_again(query)
    await basic.start(update,context)
    return -1