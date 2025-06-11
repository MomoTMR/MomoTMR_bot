import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

LNG_TRANSLATE = {
    "spain" : {
        "name" : "Переводчик на Испанский",
        "emoji": "🇪🇸",
        "prompt": """Ты перерводчик лингвист русско-испансокого языка, можешь легко в литературном стиле, выдать перевод туда и обратно, я хочу получить исходное предложение и его перевод"""
    },
    "china" : {
            "name" : "Переводчик на Китайский",
            "emoji": "🇨🇳",
            "prompt": """Ты перерводчик лингвист русско-китайского языка, можешь легко в литературном стиле, выдать перевод туда и обратно, я хочу получить исходное предложение и его перевод"""
    },
    "germany" : {
            "name" : "Переводчик на Немецкий",
            "emoji": "🇩🇪",
            "prompt": """Ты перерводчик лингвист русско-немецкого языка, можешь легко в литературном стиле, выдать перевод туда и обратно, я хочу получить исходное предложение и его перевод"""
    },
    "english" : {
            "name" : "Переводчик на Американский",
            "emoji": "🇺🇸",
            "prompt": """Ты перерводчик лингвист русско-английского языка, можешь легко в литературном стиле, выдать перевод туда и обратно, я хочу получить исходное предложение и его перевод"""
    },
}

def get_translate_keyboard():
    """Клавиатура для обработки чата c переводами"""

    keyboard = []
    for key, languages in LNG_TRANSLATE.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{languages['emoji']} {languages['name']}",
                callback_data = f"languages_{key}"
            )
        ])
    keyboard.append([InlineKeyboardButton("Вернутся в главное меню", callback_data="finish_translate")])
    return InlineKeyboardMarkup(keyboard)

def get_languages_data(languages_key):
    "Получить данные о языке перевода по ключу"
    logging.info(f" Выбран язык {languages_key}")
    return LNG_TRANSLATE.get(languages_key)