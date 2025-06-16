from dotenv import load_dotenv
from telegram.ext import (CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler,
                          ApplicationBuilder,
                          CallbackContext, ContextTypes)
from telegram import Update
import os
import logging

from services import voice_recognition

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
VOICE_DIALOG = 1

CAPTION_VOICE = "Отправьте голосовое сообщение, и я отвечу голосом!"


async def start_voice_dialog(update: Update, context: CallbackContext) -> int:

    logger.info("Начинает диалог с голосовыми сообщениями.")
    context.user_data['gpt_history'] = []  # Инициализация истории
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


# async def handle_voice(update: Update, context: CallbackContext) -> int:
#     voice = update.message.voice
#     file = await voice.get_file()
#     file_path = f"voice_{update.message.message_id}.ogg"
#     await file.download_to_drive(file_path)
#
#     # Конвертируем ogg в wav для распознавания
#     audio = AudioSegment.from_ogg(file_path)
#     wav_file = "voice.wav"
#     audio.export(wav_file, format="wav")
#
#     # Распознаем речь
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(wav_file) as source:
#         audio_data = recognizer.record(source)
#         try:
#             text = recognizer.recognize_google(audio_data, language="ru-RU")
#             response_text = f"Вы сказали: {text}"
#         except sr.UnknownValueError:
#             response_text = "Не удалось распознать голос."
#         except sr.RequestError:
#             response_text = "Ошибка сервиса распознавания."
#
#     # Создаем голосовой ответ
#     tts = gTTS(text=response_text, lang='ru')
#     tts_file = "response.mp3"
#     tts.save(tts_file)
#     audio = AudioSegment.from_mp3(tts_file)
#     voice_response_file = "response.ogg"
#     audio.export(voice_response_file, format="ogg", codec="libopus")
#
#     with open(voice_response_file, 'rb') as voice_file:
#         await update.message.reply_voice(voice=voice_file)
#
#     os.remove(file_path)
#     os.remove(wav_file)
#     os.remove(tts_file)
#     os.remove(voice_response_file)
#
#     return VOICE_DIALOG


async def cancel(update: Update, context: CallbackContext) -> int:
    """Завершает диалог."""
    await update.message.reply_text("Диалог завершен.")
    return ConversationHandler.END


def main():
    # Подулючаем переменной из окружения ".env"
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("Введите TELEGRAM_TOKEN токен в файле .env")
    else:
        logger.debug("TELEGRAM_TOKEN loaded successfully")

    # Замените 'YOUR_TOKEN' на ваш токен
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Создаем ConversationHandler для голосового диалога
    voice_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('voice', start_voice_dialog)],
        states={
            VOICE_DIALOG: [
                MessageHandler(filters.VOICE, voice_recognition.handle_voice),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчик в приложение
    application.add_handler(voice_conv_handler)

    # Запускаем бота
    application.run_polling()


if __name__ == '__main__':
    main()