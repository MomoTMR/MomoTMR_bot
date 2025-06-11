import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

async def handle_voice(update: Update, context: CallbackContext) -> int:
    voice = update.message.voice
    file = await voice.get_file()
    file_path = f"voice_{update.message.message_id}.ogg"
    await file.download_to_drive(file_path)

    # Конвертируем ogg в wav для распознавания
    audio = AudioSegment.from_ogg(file_path)
    wav_file = "voice.wav"
    audio.export(wav_file, format="wav")

    # Распознаем речь
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            response_text = f"Вы сказали: {text}"
        except sr.UnknownValueError:
            response_text = "Не удалось распознать голос."
        except sr.RequestError:
            response_text = "Ошибка сервиса распознавания."

    # Создаем голосовой ответ
    tts = gTTS(text=response_text, lang='ru')
    tts_file = "response.mp3"
    tts.save(tts_file)
    audio = AudioSegment.from_mp3(tts_file)
    voice_response_file = "response.ogg"
    audio.export(voice_response_file, format="ogg", codec="libopus")

    with open(voice_response_file, 'rb') as voice_file:
        await update.message.reply_voice(voice=voice_file)

    os.remove(file_path)
    os.remove(wav_file)
    os.remove(tts_file)
    os.remove(voice_response_file)

    return VOICE_DIALOG