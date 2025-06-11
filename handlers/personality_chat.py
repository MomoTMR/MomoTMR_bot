import logging
from statistics import quantiles

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, ConversationHandler
import os

from data.personalities import get_personality_data, get_personality_keyboard
from handlers import basic
from services.openai_client import get_personality_response

logger = logging.getLogger(__name__)

SELECTION_PERSONALITY, CHATING_WITH_PERSONALITY = range(2)

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Обработка команды /talk")
    await talk_start(update,context)

async def talk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Обработка кнопки talk_interface")
    try:
        image_path="data/images/personality.png"
        message_text = (
            "Диалог с известной личностью\n\n"
            "Выберете с кем хотите общаться\n\n"
            "Выберите личность:"
        )

        keyboard = get_personality_keyboard()

        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                if update.callback_query:
                    await update.callback_query.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                else:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
        else:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
        if update.callback_query:
            await update.callback_query.answer()

        return SELECTION_PERSONALITY

    except Exception as e:
        logger.error(f"Ошибка при запуске диалога с лчиностями {e}")
        error_text = "Erorr at startup! Try later"

        if update.callback_query.edit_message_text(error_text):
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)

        return -1


async def personality_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Обработка выбора личности")
    query = update.callback_query
    await query.answer()

    try:
        logging.info(f"Извлекаем ключ личности из callback_data")
        personality_key = query.data.replace("personality_","")
        personality = get_personality_data(personality_key)
        logging.info(f"Проерка переменной {personality}")
        if not personality:
            await query.edit_message_text("X Ошибка: Личность не найдена.")
            return -1

        context.user_data['current_personality'] = personality_key
        context.user_data['personality_data'] = personality
        logging.info(f"Сохраняем выбраную личность в контексте -{personality}")
        message_text = (
            f"{personality['emoji']} Диалог с {personality['name']} \n\n"
            f"Теперь вы можете общатся с {personality['name']}! \n\n"
            f"Просто напишите сообщение и личность ответит вам в своем стиле\n\n"
            f"Напишите что нибудь:"
        )

        await query.edit_message_text(message_text)

        return CHATING_WITH_PERSONALITY

    except Exception as e:
        logger.error(f"Erorr choose personality {e}")
        await query.edit_message_text("To be error. PLease try again.")
        return SELECTION_PERSONALITY

async def handle_personality_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщения для личности"""
    logger.info(f"Получено сообщение в Personality: {update.message.text}")
    try:
        user_message = update.message.text
        personality_key = context.user_data.get('current_personality')
        personality_data = context.user_data.get('personality_data')

        if not personality_key or not personality_data:
            await update.message.reply_text(
                f"Произошла ошибка: личность не выбрана. Используйте /talk для начала {personality_key} {personality_data}"
            )
            return SELECTION_PERSONALITY

        # Показываем индикатор "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        #Отправляем сообщение о том , что обрабатываем запрос
        processing_msg = await update.message.reply_text(
            f"{personality_data['emoji']} {personality_data['name']} размышляет"
        )

        personality_response = await get_personality_response(user_message,personality_data['prompt'])

        #Создаем кнопки
        keyboard = [
            # [InlineKeyboardButton('Продолжить диалог', callback_data="continue_chat")],
            [InlineKeyboardButton('Выбрать другую личность', callback_data="change_personality")],
            [InlineKeyboardButton('Закончить', callback_data="finish_talk")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        #Удаляем сообщение обработки и отправляем ответ.
        await processing_msg.delete()
        await update.message.reply_text(
            f"{personality_data['emoji']} {personality_data['name']} отвечает: {personality_response}",
            parse_mode = 'HTML',
            reply_markup=reply_markup
        )

        return CHATING_WITH_PERSONALITY
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения для личности {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке сообщения. Попробуйте еще раз"
        )
        return  -1

async def handle_personality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    logger.info(f"Получен callback в Personality: {query.data}")
    await query.answer()

    if query.data == "continue_chat":
        personality_data = context.user_data.get("personality_data")
        if personality_data:
            pass # Заглушка на перезапуск диалога.
            logger.info("Здесь продолжение диалога с той же личностью")
        return CHATING_WITH_PERSONALITY

    elif query.data == "change_personality":
        context.user_data.pop('current_personality', None)
        context.user_data.pop('personality_data', None)
        await talk_start(update,context)
        return SELECTION_PERSONALITY

    elif query.data == "finish_talk":
        logging.info(f"Очищаем личности {query.data}")
        context.user_data.clear()
        context.user_data.pop('current_personality',None)
        context.user_data.pop('personality_data',None)
        await basic.start(update, context)
        return  ConversationHandler.END

    return CHATING_WITH_PERSONALITY
