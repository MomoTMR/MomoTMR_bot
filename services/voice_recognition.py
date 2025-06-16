import os
import logging
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


async def handle_voice(update: Update, context: CallbackContext) -> int:
    """Обработка голосовых сообщений с распознаванием и ответом"""
    file_path = None
    wav_file = None
    tts_file = None
    voice_response_file = None

    try:
        logger.info(f"Получено голосовое сообщение от пользователя {update.effective_user.id}")

        voice = update.message.voice
        file = await voice.get_file()
        file_path = f"voice_{update.message.message_id}.ogg"
        await file.download_to_drive(file_path)
        logger.info(f"Голосовое сообщение сохранено: {file_path}")

        # Конвертируем ogg в wav для распознавания
        try:
            audio = AudioSegment.from_ogg(file_path)
            wav_file = f"voice_{update.message.message_id}.wav"
            audio.export(wav_file, format="wav")
            logger.info("Аудио конвертировано в WAV формат")
        except Exception as e:
            logger.error(f"Ошибка конвертации аудио: {e}")
            await update.message.reply_text("Ошибка обработки аудиофайла.")
            return -1

        # Распознаем речь
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(wav_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="ru-RU")
                response_text = f"Вы сказали: {text}"
                logger.info(f"Распознанный текст: {text}")
        except sr.UnknownValueError:
            response_text = "Не удалось распознать голос. Попробуйте говорить четче."
            logger.warning("Голос не распознан")
        except sr.RequestError as e:
            response_text = "Ошибка сервиса распознавания. Попробуйте позже."
            logger.error(f"Ошибка сервиса распознавания: {e}")

        # Создаем голосовой ответ
        try:
            tts = gTTS(text=response_text, lang='ru')
            tts_file = f"response_{update.message.message_id}.mp3"
            tts.save(tts_file)
            logger.info("TTS аудио создано")

            audio = AudioSegment.from_mp3(tts_file)
            voice_response_file = f"response_{update.message.message_id}.ogg"
            audio.export(voice_response_file, format="ogg", codec="libopus")
            logger.info("Голосовой ответ готов")

            with open(voice_response_file, 'rb') as voice_file:
                await update.message.reply_voice(voice=voice_file)
                logger.info("Голосовой ответ отправлен")

        except Exception as e:
            logger.error(f"Ошибка создания голосового ответа: {e}")
            await update.message.reply_text(response_text)

    except Exception as e:
        logger.error(f"Общая ошибка обработки голоса: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при обработке голосового сообщения.")

    finally:
        # Очищаем временные файлы
        temp_files = [file_path, wav_file, tts_file, voice_response_file]
        for temp_file in temp_files:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.debug(f"Удален временный файл: {temp_file}")
                except Exception as e:
                    logger.warning(f"Не удалось удалить файл {temp_file}: {e}")
