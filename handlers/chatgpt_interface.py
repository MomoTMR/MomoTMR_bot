import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from services.openai_client import get_chatgpt_response
import os

logger = logging.getLogger(__name__)


WAITING_FOR_MESSAGE = 1
# Задаем кнопки для inline keyboard.
keyboard = [
    [InlineKeyboardButton("💬 Задать еще вопрос", callback_data="gpt_continue")],
    [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="gpt_finish")]
]

# Кдадем клаиши в переменную reply_markup
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
    "✍️ Просто напишите ваш вопрос следующим сообщением:"
)


async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /gpt"""
    logger.info("Запуск обработки GPT")
    await gpt_start(update, context)


async def gpt_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        query = update.callback_query
        logger.info(f"Старт обработки GPT Response{query.data}")

        image_path = "data/images/chatgpt.png"

        if update.callback_query:
            query = update.callback_query
            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    sent_message = await query.message.edit_media(
                        media=InputMediaPhoto(media=photo, caption=CAPTION, parse_mode='HTML'),
                        # reply_markup=reply_markup
                    )
            else:
                sent_message = await query.message.edit_text(
                    text=CAPTION,
                    parse_mode='HTML',
                    # reply_markup=reply_markup
                )
            await query.answer()
        else:
            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    sent_message = await update.message.reply_photo(
                        photo=photo,
                        caption=CAPTION,
                        parse_mode='HTML',
                        # reply_markup=reply_markup
                    )
            else:
                sent_message = await update.message.reply_text(
                    CAPTION,
                    parse_mode='HTML',
                    # reply_markup=reply_markup
                )

        # Сохраняем ID сообщения для последующего удаления
        context.user_data['gpt_message_id'] = sent_message.message_id

        return WAITING_FOR_MESSAGE

    except Exception as e:
        logger.error(f"Ошибка при запуске ChatGPT интерфейса: {e}", exc_info=True)
        error_text = "😔 Произошла ошибка при запуске ChatGPT интерфейса. Попробуйте позже."
        if update.callback_query:
            await update.callback_query.message.reply_text(error_text)
        else:
            await update.message.reply_text(error_text)
        return -1

async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"Запуск обработки сообщения для ChatGPT: {update.message.text}")
    try:
        user_message = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        processing_msg = await update.message.reply_text("🤔 Обрабатываю ваш запрос... ⏳")

        # Отправляем запрос пользователя в ChatGPT -> openai_client
        gpt_response = await get_chatgpt_response(user_message)

        logger.info(f"Получен ответ от ChatGPT: {gpt_response}")

        # Удаляем сообщение пользователя
        await update.message.delete()

        # Удаляем предыдущее сообщение с меню, если оно есть
        await processing_msg.delete()

        if 'gpt_message_id' in context.user_data:
            logger.info(f"Контекст сообщения в {context.user_data['gpt_message_id']}")
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['gpt_message_id']
                )
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение с меню: {e}")

        return WAITING_FOR_MESSAGE

        # Отправляем новое сообщение "ChatGPT отвечает:"
        sent_message = await update.message.reply_text(
            f"🤖 <b>ChatGPT отвечает:</b>\n\n{gpt_response}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        # Сохраняем ID нового сообщения в context,user_data
        context.user_data['gpt_message_id'] = sent_message.message_id
        logger.info(f"Получен ответ от ChatGPT: {context.user_data['gpt_message_id']}")

        return WAITING_FOR_MESSAGE #Остаемся в диалоге

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения для ChatGPT: {e}", exc_info=True)
        await update.message.reply_text(
            "😔 Произошла ошибка при обработке вашего сообщения. Попробуйте еще раз или вернитесь в главное меню."
        )
        return -1 # Выход из Диалога