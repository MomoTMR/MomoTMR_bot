"""
Модуль для работы с темами квизов.

Содержит конфигурацию различных тем для квизов, включая промпты для генерации
вопросов с помощью ChatGPT. Каждая тема имеет название, эмодзи и специализированный
промпт для создания вопросов соответствующей тематики.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

QUIZ_TOPICS = {
    "programming": {
        "name": "💻 Программирование",
        "emoji": "💻",
        "prompt": """Ты создаешь вопросы для квиза по программированию.
Создай один интересный вопрос средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    },
    "history": {
        "name": "🏛️ История",
        "emoji": "🏛️",
        "prompt": """Ты создаешь вопросы для квиза по истории.
Создай один интересный исторический вопрос средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    },
    "science": {
        "name": "🔬 Наука",
        "emoji": "🔬",
        "prompt": """Ты создаешь вопросы для квиза по науке (физика, химия, биология).
Создай один интересный научный вопрос средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    },
    "geography": {
        "name": "🌍 География",
        "emoji": "🌍",
        "prompt": """Ты создаешь вопросы для квиза по географии.
Создай один интересный географический вопрос средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    },
    "movies": {
        "name": "🎬 Кино",
        "emoji": "🎬",
        "prompt": """Ты создаешь вопросы для квиза о кино и фильмах.
Создай один интересный вопрос о фильмах средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    }
}


def get_quiz_topics_keyboard():
    """
    Создает клавиатуру с доступными темами квизов.

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками тем квизов и возврата в главное меню
    """
    keyboard = []
    for topic_key, topic_data in QUIZ_TOPICS.items():
        keyboard.append([InlineKeyboardButton(topic_data["name"], callback_data=f"quiz_topic_{topic_key}")])

    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="quiz_finish")])
    return InlineKeyboardMarkup(keyboard)


def get_quiz_topic_data(topic_key):
    """
    Получить данные о теме квиза по ключу.

    Args:
        topic_key (str): Ключ темы из словаря QUIZ_TOPICS

    Returns:
        dict: Данные о теме (name, emoji, prompt) или None если ключ не найден
    """
    return QUIZ_TOPICS.get(topic_key)


def get_quiz_continue_keyboard(topic_key):
    """
    Создает клавиатуру для продолжения квиза после ответа на вопрос.

    Args:
        topic_key (str): Ключ текущей темы квиза

    Returns:
        InlineKeyboardMarkup: Клавиатура с опциями продолжения квиза
    """
    logger.info(f"Топик {topic_key}")
    keyboard = [
        [InlineKeyboardButton("🎯 Ещё вопрос", callback_data=f"quiz_continue_{topic_key}")],
        [InlineKeyboardButton("🔄 Сменить тему", callback_data="quiz_change_topic")],
        [InlineKeyboardButton("🏁 Закончить квиз", callback_data="quiz_finish")]
    ]
    return InlineKeyboardMarkup(keyboard)
