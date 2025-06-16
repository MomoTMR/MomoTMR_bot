from dotenv import load_dotenv
from telegram.ext import (
                          ConversationHandler,
                          CallbackContext, ContextTypes)
from telegram import Update
import os
import logging
from handlers import basic


# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
VOICE_DIALOG: int = 1

# Задаем текст для отправки пользователю.
CAPTION_VOICE = "Отправьте голосовое сообщение, и я отвечу голосом!"

async def start_voice_dialog(update: Update, context: CallbackContext) -> int:

    logger.info("Начинает диалог с голосовыми сообщениями.")
    context.user_data['voice_history'] = []  # Очистка истории
    await send_voice_menu(update, context)
    return VOICE_DIALOG

async def send_voice_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    image_path = "data/images/voice_chat.png"
    caption = CAPTION_VOICE

    # Удаляем всё лишнее
    if update.message:
        await update.message.delete()

    if update.callback_query:
        query = update.callback_query
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                sent = await query.message.edit_media(
                    media=InputMediaPhoto(media=photo, caption=caption, parse_mode='HTML'),
                )
        else:
            sent = await query.message.edit_text(
                text=caption,
                parse_mode='HTML',
            )
        await query.answer()
    else:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                sent = await update.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    parse_mode='HTML',
                )
        else:
            sent = await update.message.reply_text(
                caption,
                parse_mode='HTML',
            )

    # Сохраняем ID, чтобы удалить позже
    context.user_data['gpt_message_id'] = sent.message_id


async def voice_cancel(update: Update, context: CallbackContext) -> int:
    """Завершает диалог."""
    # await update.message.reply_text("Диалог завершен.")
    await basic.start(update,context)
    return ConversationHandler.END