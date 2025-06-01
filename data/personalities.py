from telegram import InlineKeyboardButton, InlineKeyboardMarkup

PERSONALITIES = {
    "einstein" : {
        "name": "Альберт Эйнштейн",
        "emoji": "⚙️",
        'prompt': (
            "Ты - Альберт эйнштейн..."
            "..."
        )
    },
    "shekspeare": {
        "name": "Уильям Шекспир",
        "emoji": "⚙️",
        "prompt": (
            "Ты - Уильям Шекспир..."
            "..."
        )
    }
}

def get_personality_keyboard():
    """Клавиатура для обработки персонолаьного чата"""

    keyboard = []
    for key, personality in PERSONALITIES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{personality['emoji']} {personality['name']}",
                callback_data = f"personality_{key}"
            )
        ])
    keyboard.append([InlineKeyboardButton("Back to Home menu", callback_data="main_menu")])

    return InlineKeyboardMarkup(keyboard)

def get_personality_data(personality_key):
    "Получить данные о личности по ключу"
    return PERSONALITIES.get(personality_key)