# TelegramBot с интегрированным ChatGPT

Многофункциональный Telegram-бот с поддержкой ChatGPT, голосового взаимодействия, переводчика, квизов и диалогов с известными личностями.

## 🚀 Функции

- **ChatGPT интеграция** - общение с искусственным интеллектом
- **Голосовые сообщения** - распознавание речи и голосовые ответы
- **Переводчик** - перевод на различные языки
- **Квизы** - интерактивные викторины по разным темам
- **Диалоги с личностями** - общение с известными персонажами
- **Случайные факты** - получение интересных фактов

## 📋 Требования

- Python 3.8+
- Telegram Bot Token
- OpenAI API Key
- Системные библиотеки для аудио обработки

## 🛠 Установка

### 🚀 Быстрая установка (с использованием Makefile)

```bash
git clone <repository-url>
cd MyTelegramBot

# Полная автоматическая установка
make setup
```

Эта команда выполнит:
- Установку системных зависимостей
- Создание виртуального окружения
- Установку Python пакетов
- Создание файла .env
- Проверку установки

### 📋 Пошаговая установка

#### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd MyTelegramBot
```

#### 2. Создание виртуального окружения

```bash
python -m venv .venv
```

**Активация виртуального окружения:**

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

#### 3. Установка системных зависимостей

**С использованием Makefile (Linux/macOS):**
```bash
make install-system
```

**Вручную:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install -y ffmpeg portaudio19-dev python3-dev
```

**macOS:**
```bash
brew install ffmpeg portaudio
```

**Windows:**
- Установите ffmpeg с [официального сайта](https://ffmpeg.org/download.html#build-windows)
- Или используйте: `choco install ffmpeg` / `winget install FFmpeg`

#### 4. Установка Python зависимостей

**С использованием Makefile:**
```bash
make install
```

**Вручную:**
```bash
pip install -r requirements.txt
```

#### 5. Настройка переменных окружения

**С использованием Makefile:**
```bash
make env-example
```

**Вручную:**
```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

#### Получение токенов:

1. **Telegram Bot Token:**
   - Напишите [@BotFather](https://t.me/botfather) в Telegram
   - Отправьте команду `/newbot`
   - Следуйте инструкциям для создания бота
   - Скопируйте полученный токен

2. **OpenAI API Key:**
   - Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
   - Перейдите в раздел API Keys
   - Создайте новый API ключ
   - Скопируйте ключ в файл конфигурации

## ✅ Проверка установки

Перед запуском рекомендуется проверить, что все компоненты установлены корректно:

**С использованием Makefile:**
```bash
make check
```

**Вручную:**
```bash
python check_installation.py
```

Этот скрипт проверит:
- Версию Python и зависимости
- Системные утилиты (ffmpeg, ffprobe)
- Структуру проекта
- Конфигурацию (.env файл)
- Возможность импорта модулей
- Работу аудио обработки

## 🚀 Запуск

**С использованием Makefile:**
```bash
make run          # Обычный запуск
make run-dev      # Запуск с подробным логированием
```

**Вручную:**
```bash
python bot.py
```

## 🔧 Полезные команды Makefile

```bash
make help         # Показать все доступные команды
make info         # Информация о системе и проекте
make clean        # Очистка временных файлов
make test         # Запуск тестов
make setup        # Полная настройка проекта с нуля
```

## 🎯 Использование

1. Запустите бота командой `/start`
2. Выберите нужную функцию из главного меню
3. Следуйте инструкциям бота

### Доступные команды:

- `/start` - Главное меню
- `/voice` - Запуск голосового чата

## 🔧 Конфигурация

### Голосовые функции

Бот поддерживает:
- Распознавание речи через Google Speech Recognition
- Синтез речи через Google Text-to-Speech (gTTS)
- Обработку аудиофайлов в форматах OGG, WAV, MP3

### Дополнительные настройки

Для работы с микрофоном (если планируется расширение функциональности):

```bash
pip install PyAudio
```

**Примечание:** PyAudio может потребовать дополнительной настройки на некоторых системах.

## 📁 Структура проекта

```
MyTelegramBot/
├── bot.py                 # Главный файл бота
├── requirements.txt       # Python зависимости
├── .env.example          # Пример файла конфигурации
├── README.md             # Документация
├── handlers/             # Обработчики команд
│   ├── basic.py         # Базовые команды
│   ├── chatgpt_interface.py
│   ├── personality_chat.py
│   ├── quiz.py
│   ├── translator_chat.py
│   └── voice_chat.py
├── services/            # Сервисы
│   ├── openai_client.py
│   └── voice_recognition.py
└── data/               # Данные конфигурации
    ├── languages.py
    ├── personalities.py
    └── quiz_topics.py
```

## 🐛 Устранение неполадок

### Проблемы с аудио

1. **Ошибка "Couldn't find ffmpeg":**
   ```bash
   # Linux/macOS
   which ffmpeg
   
   # Windows
   where ffmpeg
   ```
   Если команда не найдена, переустановите ffmpeg согласно инструкциям выше.

2. **Проблемы с PyAudio:**
   - Linux: `sudo apt install portaudio19-dev python3-dev`
   - macOS: `brew install portaudio`
   - Windows: используйте предварительно скомпилированные wheels

3. **Проблемы с распознаванием речи:**
   - Проверьте интернет-соединение (используется Google Speech Recognition)
   - Убедитесь, что аудиофайл не поврежден

### Проблемы с API

1. **OpenAI API ошибки:**
   - Проверьте корректность API ключа
   - Убедитесь, что у вас есть кредиты на аккаунте OpenAI
   - Проверьте лимиты API

2. **Telegram Bot ошибки:**
   - Убедитесь, что токен бота корректный
   - Проверьте, что бот не заблокирован

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

Если у вас возникли вопросы или проблемы, создайте Issue в репозитории проекта.

## 🔄 Обновления

Чтобы обновить зависимости:

**С использованием Makefile:**
```bash
make clean-all    # Удаление старого окружения
make install      # Переустановка
```

**Вручную:**
```bash
pip install -r requirements.txt --upgrade
```

Чтобы обновить системные зависимости:

```bash
# Linux
sudo apt update && sudo apt upgrade ffmpeg

# macOS  
brew upgrade ffmpeg

# Windows (через chocolatey)
choco upgrade ffmpeg
```
