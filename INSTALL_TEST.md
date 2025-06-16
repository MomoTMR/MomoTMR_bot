# Тестирование установки

Этот файл поможет вам проверить, что все компоненты установлены корректно.

## 🧪 Быстрая проверка

Выполните следующие команды для проверки основных компонентов:

### 1. Проверка Python зависимостей

```bash
python -c "
import sys
print(f'Python версия: {sys.version}')

# Проверка основных библиотек
try:
    import telegram
    print('✅ python-telegram-bot установлен')
    print(f'   Версия: {telegram.__version__}')
except ImportError as e:
    print('❌ python-telegram-bot НЕ установлен')
    print(f'   Ошибка: {e}')

try:
    import openai
    print('✅ openai установлен')
    print(f'   Версия: {openai.__version__}')
except ImportError as e:
    print('❌ openai НЕ установлен')
    print(f'   Ошибка: {e}')

try:
    from dotenv import load_dotenv
    print('✅ python-dotenv установлен')
except ImportError as e:
    print('❌ python-dotenv НЕ установлен')
    print(f'   Ошибка: {e}')
"
```

### 2. Проверка аудио библиотек

```bash
python -c "
# Проверка аудио зависимостей
try:
    import speech_recognition as sr
    print('✅ SpeechRecognition установлен')
    print(f'   Версия: {sr.__version__}')
except ImportError as e:
    print('❌ SpeechRecognition НЕ установлен')
    print(f'   Ошибка: {e}')

try:
    from gtts import gTTS
    print('✅ gTTS установлен')
except ImportError as e:
    print('❌ gTTS НЕ установлен')
    print(f'   Ошибка: {e}')

try:
    from pydub import AudioSegment
    print('✅ pydub установлен')
    print('   Проверка ffmpeg...')
    # Эта строка покажет предупреждение, если ffmpeg не найден
    audio = AudioSegment.empty()
    print('✅ ffmpeg найден и работает корректно')
except ImportError as e:
    print('❌ pydub НЕ установлен')
    print(f'   Ошибка: {e}')
except Exception as e:
    print('⚠️  pydub установлен, но есть проблемы с ffmpeg')
    print(f'   Ошибка: {e}')
"
```

### 3. Проверка системных утилит

```bash
# Проверка ffmpeg
echo "Проверка ffmpeg:"
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✅ ffmpeg установлен"
    ffmpeg -version | head -1
else
    echo "❌ ffmpeg не найден в PATH"
fi

# Проверка ffprobe
echo -e "\nПроверка ffprobe:"
if command -v ffprobe >/dev/null 2>&1; then
    echo "✅ ffprobe установлен"
    ffprobe -version | head -1
else
    echo "❌ ffprobe не найден в PATH"
fi
```

### 4. Проверка конфигурации

```bash
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

print('Проверка файла .env:')
if os.path.exists('.env'):
    print('✅ .env файл найден')
    
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    if telegram_token and telegram_token != 'your_telegram_bot_token_here':
        print('✅ TELEGRAM_TOKEN настроен')
    else:
        print('❌ TELEGRAM_TOKEN не найден или не настроен')
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your_openai_api_key_here':
        print('✅ OPENAI_API_KEY настроен')
    else:
        print('❌ OPENAI_API_KEY не найден или не настроен')
else:
    print('❌ .env файл не найден')
    print('   Создайте .env файл на основе .env.example')
"
```

## 🚀 Тест импорта модулей

```bash
python -c "
print('Тестирование импорта модулей бота...')

try:
    from handlers import basic, chatgpt_interface, personality_chat, quiz, translator_chat, voice_chat
    print('✅ Все handlers импортированы успешно')
except ImportError as e:
    print('❌ Ошибка импорта handlers')
    print(f'   Ошибка: {e}')

try:
    from services import openai_client, voice_recognition
    print('✅ Все services импортированы успешно')
except ImportError as e:
    print('❌ Ошибка импорта services')
    print(f'   Ошибка: {e}')

try:
    from data import languages, personalities, quiz_topics
    print('✅ Все data модули импортированы успешно')
except ImportError as e:
    print('❌ Ошибка импорта data модулей')
    print(f'   Ошибка: {e}')

print('\\n🎉 Тест импорта завершен!')
"
```

## 🔧 Тест обработки аудио

Создайте тестовый аудиофайл и попробуйте его обработать:

```bash
python -c "
import os
from pydub import AudioSegment
from pydub.generators import Sine

print('Создание тестового аудиофайла...')

# Создаем тестовый тон 440 Гц на 2 секунды
tone = Sine(440).to_audio_segment(duration=2000)

# Сохраняем в разных форматах
try:
    tone.export('test_audio.wav', format='wav')
    print('✅ WAV файл создан успешно')
    
    tone.export('test_audio.mp3', format='mp3')
    print('✅ MP3 файл создан успешно')
    
    tone.export('test_audio.ogg', format='ogg')
    print('✅ OGG файл создан успешно')
    
    # Тестируем загрузку обратно
    wav_audio = AudioSegment.from_wav('test_audio.wav')
    mp3_audio = AudioSegment.from_mp3('test_audio.mp3')
    ogg_audio = AudioSegment.from_ogg('test_audio.ogg')
    
    print('✅ Все форматы загружаются корректно')
    
    # Очистка
    os.remove('test_audio.wav')
    os.remove('test_audio.mp3') 
    os.remove('test_audio.ogg')
    print('✅ Тестовые файлы удалены')
    
except Exception as e:
    print(f'❌ Ошибка обработки аудио: {e}')
"
```

## 🌐 Тест API соединений

```bash
python -c "
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_apis():
    print('Тестирование API соединений...')
    
    # Тест OpenAI API
    try:
        import openai
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            client = openai.OpenAI(api_key=openai_key)
            
            # Простой тест запроса
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': 'Test'}],
                max_tokens=5
            )
            print('✅ OpenAI API работает корректно')
        else:
            print('⚠️  OpenAI API ключ не настроен - тест пропущен')
            
    except Exception as e:
        print(f'❌ Ошибка OpenAI API: {e}')
    
    # Тест Telegram Bot API
    try:
        from telegram import Bot
        
        telegram_token = os.getenv('TELEGRAM_TOKEN')
        if telegram_token and telegram_token != 'your_telegram_bot_token_here':
            bot = Bot(token=telegram_token)
            bot_info = await bot.get_me()
            print(f'✅ Telegram Bot API работает: @{bot_info.username}')
        else:
            print('⚠️  Telegram токен не настроен - тест пропущен')
            
    except Exception as e:
        print(f'❌ Ошибка Telegram Bot API: {e}')

# Запуск асинхронного теста
asyncio.run(test_apis())
"
```

## 📋 Чек-лист готовности

Отметьте выполненные пункты:

- [ ] Python 3.8+ установлен
- [ ] Виртуальное окружение создано и активировано
- [ ] Все Python зависимости установлены (`pip install -r requirements.txt`)
- [ ] ffmpeg и ffprobe установлены и доступны в PATH
- [ ] Файл `.env` создан и настроен
- [ ] TELEGRAM_TOKEN получен от @BotFather и добавлен в `.env`
- [ ] OPENAI_API_KEY получен и добавлен в `.env`
- [ ] Все тесты импорта пройдены успешно
- [ ] Тест обработки аудио прошел успешно
- [ ] API соединения работают корректно

## 🐛 Устранение проблем

### Если тесты не проходят:

1. **Ошибки импорта Python библиотек:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **ffmpeg не найден:**
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Скачайте с [ffmpeg.org](https://ffmpeg.org/) и добавьте в PATH

3. **Проблемы с виртуальным окружением:**
   ```bash
   deactivate
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # или .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

4. **Ошибки API:**
   - Проверьте правильность токенов в `.env`
   - Убедитесь, что у вас есть интернет соединение
   - Проверьте лимиты API и баланс аккаунта

## ✅ Если все тесты прошли успешно

Поздравляем! Ваша установка готова к работе. Запустите бота:

```bash
python bot.py
```
