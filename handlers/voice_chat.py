"""
Обработчик голосового чата.

Этот модуль реализует conversation handler для голосового общения с ChatGPT.
Поддерживает:
- Прием голосовых сообщений от пользователя
- Распознавание речи с помощью Google Speech Recognition
- Отправку текста в ChatGPT и получение ответа
- Синтез речи и отправку голосового ответа пользователю
- Ведение истории диалога в рамках сессии

Состояния conversation handler:
- VOICE_DIALOG: активный режим голосового диалога

Интегрируется с services.voice_recognition для обработки аудио.
"""

from dotenv import load_dotenv
from telegram.ext import (
                          ConversationHandler,
                          CallbackContext, ContextTypes)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import os
import logging
from handlers import basic

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния диалога
VOICE_DIALOG: int = 1

# Задаем текст для отправки пользователю.
CAPTION_VOICE = (
    "🎤 <b>Голосовой чат с ChatGPT</b>\n\n"
    "📱 Отправьте голосовое сообщение, и я отвечу голосом!\n\n"
    "💡 <b>Как это работает:</b>\n"
    "1. Отправьте голосовое сообщение\n"
    "2. Я распознаю вашу речь\n"
    "3. Отправлю текст в ChatGPT\n"
    "4. Получу ответ и озвучу его\n\n"
    "🗣️ Говорите четко и не слишком быстро для лучшего распознавания."
)

async def start_voice_dialog(update: Update, context: CallbackContext) -> int:
    """
    Запускает голосовой диалог с ChatGPT.

    Инициализирует новую сессию голосового чата, очищает историю диалога
    и отправляет приветственное меню с инструкциями.

    Args:
        update (Update): Объект обновления от Telegram
        context (CallbackContext): Контекст выполнения

    Returns:
        int: VOICE_DIALOG для перехода в состояние голосового диалога
    """
    logger.info("Начинается диалог с голосовыми сообщениями.")
    context.user_data['voice_history'] = []  # Очистка истории
    await send_voice_menu(update, context)
    return VOICE_DIALOG

async def send_voice_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет меню голосового чата с инструкциями.

    Отправляет изображение с описанием возможностей голосового чата и
    inline клавиатурой для управления.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения
    """
    image_path = "data/images/voice_chat.png"
    caption = CAPTION_VOICE

    # Создаем клавиатуру для управления
    keyboard = [
        [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="voice_stop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Удаляем предыдущее сообщение если есть
        if update.message:
            await update.message.delete()

        if update.callback_query:
            query = update.callback_query
            await query.answer()

            if os.path.exists(image_path):
                try:
                    await query.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=caption,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                    await query.message.delete()
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения в голосовом чате: {e}")
                    await query.edit_message_text(
                        text=caption,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
            else:
                await query.edit_message_text(
                    text=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        else:
            # Первый запуск
            if os.path.exists(image_path):
                try:
                    await update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=caption,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения: {e}")
                    await update.message.reply_text(
                        text=caption,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
            else:
                await update.message.reply_text(
                    text=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )

    except Exception as e:
        logger.error(f"Ошибка в send_voice_menu: {e}", exc_info=True)

async def voice_cancel(update: Update, context: CallbackContext) -> int:
    """
    Завершает голосовой диалог и возвращает в главное меню.

    Очищает данные пользователя и возвращает в главное меню бота.

    Args:
        update (Update): Объект обновления от Telegram
        context (CallbackContext): Контекст выполнения

    Returns:
        int: ConversationHandler.END для завершения conversation handler
    """
    query = update.callback_query
    if query:
        await query.answer()

    logger.info("Голосовой диалог завершен пользователем")

    # Очищаем данные пользователя
    context.user_data.clear()

    # Возвращаемся в главное меню
    await basic.start(update, context)
    return ConversationHandler.END
