from dotenv import load_dotenv
from telegram.ext import (CommandHandler,
                          MessageHandler,
                          filters,
                          ConversationHandler,
                          ApplicationBuilder)
from telegram import Update
from telegram.ext import CallbackContext
import os
import logging

from services import voice_recognition

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
VOICE_DIALOG = 1


async def start_voice_dialog(update: Update, context: CallbackContext) -> int:
    """Начинает диалог с голосовыми сообщениями."""
    await update.message.reply_text("Отправьте голосовое сообщение, и я отвечу голосом!")
    return VOICE_DIALOG


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