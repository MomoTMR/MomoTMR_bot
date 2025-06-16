# 🚀 Быстрый старт

Краткое руководство для немедленного запуска MyTelegramBot.

## ⚡ Установка за 2 минуты

### 1. Скачивание и настройка

```bash
git clone <repository-url>
cd MyTelegramBot
make setup
```

### 2. Получение токенов

**Telegram Bot Token:**
1. Напишите [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

**OpenAI API Key:**
1. Зайдите на [platform.openai.com](https://platform.openai.com/)
2. Создайте аккаунт
3. Перейдите в API Keys
4. Создайте новый ключ

### 3. Настройка конфигурации

Отредактируйте файл `.env`:

```env
TELEGRAM_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
```

### 4. Запуск

```bash
make run
```

## 🔧 Альтернативная установка (без Makefile)

```bash
# 1. Создание окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows

# 2. Установка системных утилит
# Linux:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# Скачайте ffmpeg с https://ffmpeg.org/

# 3. Установка Python пакетов
pip install -r requirements.txt

# 4. Настройка конфигурации
cp .env.example .env
# Отредактируйте .env файл

# 5. Проверка
python check_installation.py

# 6. Запуск
python bot.py
```

## ✅ Проверка работы

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Попробуйте разные функции:
   - 🤖 ChatGPT - текстовое общение с ИИ
   - 🎲 Рандомный факт - получение интересных фактов
   - 🚀 Голосовой чат - отправьте голосовое сообщение

## 🐛 Решение проблем

### Бот не отвечает
- Проверьте токен в `.env`
- Убедитесь, что бот не заблокирован
- Проверьте интернет соединение

### Ошибки с ffmpeg
```bash
# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Проверка
ffmpeg -version
```

### Ошибки с Python пакетами
```bash
pip install -r requirements.txt --force-reinstall
```

### Проблемы с голосом
- Проверьте, что ffmpeg установлен
- Убедитесь, что есть интернет (нужен для Google Speech API)

## 📱 Функции бота

| Функция | Описание |
|---------|----------|
| 🤖 ChatGPT | Общение с ИИ, генерация текста |
| 🎲 Рандомный факт | Интересные факты |
| 👥 Диалог с личностью | Чат с известными персонажами |
| 🧠 Квиз | Интерактивные викторины |
| 🥸 Переводчик | Перевод на разные языки |
| 🚀 Голосовой чат | Распознавание и синтез речи |

## 🔑 Необходимые токены

- **TELEGRAM_TOKEN** - от @BotFather (обязательно)
- **OPENAI_API_KEY** - от OpenAI (обязательно для ChatGPT)

## 📋 Системные требования

- Python 3.8+
- ffmpeg (для аудио)
- Интернет соединение
- ~50MB свободного места

## 🆘 Нужна помощь?

1. Запустите: `make check` или `python check_installation.py`
2. Посмотрите полный README.md
3. Создайте Issue в репозитории

---

**Готово!** 🎉 Ваш бот должен работать. Удачного использования!