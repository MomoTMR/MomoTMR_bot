import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
import os

from data.personalities import get_personality_data, get_personality_keyboard
from services.openai_client import get_personality_response

logger = logging.getLogger(__name__)

SELECTION_PERSONALITY, CHATING_WITH_PERSONALITY = range(2)

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /talk"""
    await talk_start(update,context)

async def talk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        image_path="data/images/chagpt.png"
        message_text = (
            "Диалог с известной личностью\n\n"
            "Выберете с кем хотите общаться\n\n"
            "Альберт Эйнштейн\n\n"
            "Уйльям Шекспир\n\n"
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
    """Обработка выбора личности"""
    query = update.callback_query
    await query.answer()

    try:
        #Извлекаем ключ личности из callback_data
        personality_key = query.data.replace("personality_","")
        personality = get_personality_data(personality_key)

        if not personality:
            await query.edit_message_text("X Ошибка: Личность не найдена.")
            return -1

        #Сохраняем выбраную личность в контексте
        context.user_data['current_personality'] = personality_key
        context.user_data['personality_data'] = personality

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
        return -1

async def handle_personality_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщения для личности"""
    try:
        user_message = update.message.text
        personality_key = context.user_data.get('current_personality')
        personality_data = context.user_data.get('personality_data')

        if not personality_key or not personality_data:
            await update.message.reply_text(
                f"Произошла ошибка: личность не выбрана. Используйте /talk для начала {personality_key} {personality_data}"
            )
            return -1

        # Показываем индикатор "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        #Отправляем сообщение о том , что обрабатываем запрос
        processing_msg = await update.message.reply_text(
            f"{personality_data['emoji']} {personality_data['name']} размышляет"
        )

        personality_response = await get_personality_response(user_message,personality_data['prompt'])

        #Создаем кнопки
        keyboard = [
            [InlineKeyboardButton('Продолжить диалог', callback_data="continue_chat")],
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
        return  CHATING_WITH_PERSONALITY

async def handle_personality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок в диалоге с личностью"""
    query = update.callback_query
    await query.answer()

    if query.data == "continue_chat":
        personality_data = context.user_data.get("personality_data")
        if personality_data:
            await query.edit_message_text(
                f"{personality_data['emoji']} Продолжаем диалог с {personality_data['name']}\n\n",
                "Напишите следующее сообщение",
                parse_mode='HTML'
            )
        return CHATING_WITH_PERSONALITY

    elif query.data == "change_personality":
        return await talk_start(update,context)

    elif query.data == "finish_talk":
        # Очищаем личности
        context.user_data.pop('current_personality',None)
        context.user_data.pop('personality_data',None)

        from handlers.basic import start
        await start(update,context)
        return  -1

    return CHATING_WITH_PERSONALITY
