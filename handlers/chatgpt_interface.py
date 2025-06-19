"""
Интерфейс для общения с ChatGPT.

Этот модуль реализует conversation handler для диалога пользователя с ChatGPT.
Поддерживает:
- Создание и отправку запросов к OpenAI API
- Сохранение истории диалога в рамках сессии
- Управление интерфейсом через inline клавиатуру
- Отправку изображений с меню интерфейса

Состояния conversation handler:
- WAITING_FOR_MESSAGE: ожидание сообщения от пользователя
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from handlers import basic
from services.openai_client import get_chatgpt_response
import os

logger = logging.getLogger(__name__)

WAITING_FOR_MESSAGE = 1

# Задаем кнопки для inline keyboard.
keyboard = [
    [InlineKeyboardButton("💬 Новый диалог с OpenAI", callback_data="gpt_continue")],
    [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="gpt_finish")]
]

# Кладем клавиши в переменную reply_markup
reply_markup = InlineKeyboardMarkup(keyboard)

# Формируем заголовок
CAPTION = (
    "🤖 <b>ChatGPT Интерфейс</b>\n\n"
    "Напишите любой вопрос или сообщение, и я передам его ChatGPT!\n\n"
    "💡 <b>Примеры вопросов:</b>\n"
    "• Объясни квантовую физику простыми словами\n"
    "• Напиши короткий рассказ про кота\n"
    "• Как приготовить пасту карбонара?\n"
    "• Переведи фразу на английский\n\n"
)

async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /gpt - запуск интерфейса ChatGPT.

    Инициализирует новую сессию диалога с ChatGPT, очищает историю и
    отправляет приветственное меню.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: WAITING_FOR_MESSAGE для перехода в состояние ожидания сообщения
    """
    logger.info("▶️ Запуск ChatGPT-интерфейса")
    context.user_data['gpt_history'] = []  # Инициализация истории
    await send_gpt_menu(update, context)
    return WAITING_FOR_MESSAGE

async def continue_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для продолжения диалога с ChatGPT (новый диалог).

    Очищает историю диалога и отправляет меню для начала нового диалога.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения

    Returns:
        int: WAITING_FOR_MESSAGE для перехода в состояние ожидания сообщения
    """
    logger.info("▶️ Перезапуск ChatGPT-интерфейса")
    context.user_data['gpt_history'] = []  # Очистка истории
    await send_gpt_menu(update, context)
    return WAITING_FOR_MESSAGE

async def send_gpt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет меню интерфейса ChatGPT с изображением и инструкциями.

    Отправляет изображение с описанием возможностей ChatGPT и inline клавиатурой.
    Если изображение не найдено, отправляет только текстовое сообщение.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения
    """
    image_path = "data/images/chatgpt.png"
    caption = CAPTION

    # Удаляем всё лишнее
    if update.message:
        await update.message.delete()

    if update.callback_query:
        query = update.callback_query
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    media = InputMediaPhoto(media=photo, caption=caption, parse_mode='HTML')
                    sent_message = await query.edit_message_media(media=media, reply_markup=reply_markup)
                    context.user_data['gpt_message_id'] = sent_message.message_id
                    await query.answer()
                    return
            except Exception as e:
                logger.error(f"Ошибка отправки изображения: {e}")

        # Фолбэк: отправляем обычное текстовое сообщение
        try:
            sent_message = await query.edit_message_text(text=caption, parse_mode='HTML', reply_markup=reply_markup)
            context.user_data['gpt_message_id'] = sent_message.message_id
            await query.answer()
        except Exception as e:
            logger.error(f"Ошибка отправки текста: {e}")
            await query.answer()
    else:
        # Первый запуск из команды
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    sent_message = await update.message.reply_photo(photo=photo, caption=caption, parse_mode='HTML', reply_markup=reply_markup)
                    context.user_data['gpt_message_id'] = sent_message.message_id
                    return
            except Exception as e:
                logger.error(f"Ошибка отправки изображения: {e}")

        # Фолбэк: отправляем обычное текстовое сообщение
        sent_message = await update.message.reply_text(text=caption, parse_mode='HTML', reply_markup=reply_markup)
        context.user_data['gpt_message_id'] = sent_message.message_id

async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик текстовых сообщений для отправки в ChatGPT.

    Получает сообщение пользователя, отправляет его в ChatGPT вместе с историей диалога,
    получает ответ и отправляет его пользователю с меню для продолжения.

    Args:
        update (Update): Объект обновления от Telegram с текстовым сообщением
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения с историей диалога

    Returns:
        int: WAITING_FOR_MESSAGE для продолжения ожидания сообщений
    """
    try:
        await delete_previous_menu(update, context)
        user_message = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Сохраняем сообщение пользователя в историю
        context.user_data['gpt_history'].append({"role": "user", "content": user_message})
        logger.info(f"Сообщение пользователя {user_message}")

        # Отправляем "обрабатываю"
        processing_msg = await update.message.reply_text("🤔 Обрабатываю ваш запрос... ⏳")

        # Получаем ответ от GPT, передавая всю историю
        logger.info(f"История диалога: {context.user_data['gpt_history']}")

        # Получаем ответ от GPT, передавая всю историю
        response_text = await get_chatgpt_response(context.user_data['gpt_history'])

        logger.info(f"Получен ответ от ChatGPT: {response_text}")

        # Сохраняем ответ GPT в историю
        context.user_data['gpt_history'].append({"role": "assistant", "content": response_text})

        # Удаляем сообщение пользователя
        await update.message.delete()

        # Удаляем сообщение о обработке OpenAI
        await processing_msg.delete()

        # Отправляем ответ с меню
        response_msg = await update.message.reply_text(
            f"🤖 <b>ChatGPT отвечает:</b>\n\n{response_text}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        # Сохраняем ID сообщения для последующего удаления
        context.user_data['gpt_message_id'] = response_msg.message_id

        return WAITING_FOR_MESSAGE

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)
        await update.message.reply_text(
            "😔 Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз."
        )
        return WAITING_FOR_MESSAGE

async def delete_previous_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Удаляет предыдущее меню ChatGPT интерфейса.

    Находит и удаляет сохраненное сообщение с меню, чтобы избежать
    накопления сообщений в чате.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст с сохраненным ID сообщения
    """
    message_id = context.user_data.get('gpt_message_id')
    if message_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
        except Exception as e:
            logger.warning(f"❗ Не удалось удалить меню: {e}")

async def finish_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None) -> int:
    """
    Завершает работу с ChatGPT интерфейсом.

    Очищает пользовательские данные и возвращает в главное меню.

    Args:
        update (Update): Объект обновления от Telegram
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения
        query: Неиспользуемый параметр для совместимости

    Returns:
        int: -1 для завершения conversation handler
    """
    query = update.callback_query
    await query.answer()

    # Удалим сохранённые данные (если надо)
    context.user_data.clear()

    await asyncio.sleep(3)
    await basic.start(update, context)
    return -1
