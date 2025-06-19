"""
Модуль data содержит конфигурационные данные для бота:
- languages.py - языки для переводчика
- personalities.py - личности для чата
- quiz_topics.py - темы для квизов
"""

from .languages import LNG_TRANSLATE, get_translate_keyboard, get_languages_data
from data.personalities import PERSONALITIES, get_personality_keyboard, get_personality_data
from .quiz_topics import QUIZ_TOPICS, get_quiz_topics_keyboard, get_quiz_topic_data, get_quiz_continue_keyboard

__all__ = [
    'LNG_TRANSLATE',
    'get_translate_keyboard',
    'get_languages_data',
    'PERSONALITIES',
    'get_personality_keyboard',
    'get_personality_data',
    'QUIZ_TOPICS',
    'get_quiz_topics_keyboard',
    'get_quiz_topic_data',
    'get_quiz_continue_keyboard'
]
