import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, ConversationHandler
import os

from data.languages import get_languages_data, get_translate_keyboard
from handlers import basic
from services.openai_client import get_personality_response

logger = logging.getLogger(__name__)

SELECTION_LANGUAGE, CHATING_WITH_TRANSLATOR = range(2)

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /translate"""
    await translate_start(update,context)
    
async def translate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        image_path="data/images/translate.png"
        message_text = (
            "Вам представлен переводчик\n\n"
            "Выберете я зык для перевода\n\n"
        )

        keyboard = get_translate_keyboard()

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

        return SELECTION_LANGUAGE

    except Exception as e:
        logger.error(f"Ошибка при запуске диалога с переводчиком {e}")
        error_text = "Erorr at startup! Try later"

        if update.callback_query.edit_message_text(error_text):
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)

        return -1

async def languages_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора личности"""
    query = update.callback_query
    await query.answer()

    try:
        #Извлекаем ключ личности из callback_data
        languages_key = query.data.replace("languages_","")
        languages = get_languages_data(languages_key)

        if not languages:
            await query.edit_message_text("X Ошибка: Личность не найдена.")
            return -1

        #Сохраняем выбраную личность в контексте
        context.user_data['current_languages'] = languages_key
        context.user_data['languages_data'] = languages

        message_text = (
            f"{languages['emoji']} Диалог с {languages['name']} \n\n"
            f"Теперь вы можете общатся с {languages['name']}! \n\n"
            f"Просто напишите сообщение и личность ответит вам в своем стиле\n\n"
            f"Напишите что нибудь:"
        )

        await query.edit_message_text(message_text)

        return CHATING_WITH_TRANSLATOR
    
    except Exception as e:
        logger.error(f"Erorr choose translator {e}")
        await query.edit_message_text("To be error. PLease try again.")
        return SELECTION_LANGUAGE
    
async def handle_languages_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщения для личности"""
    logger.info(f"Получено сообщение от Переводчика: {update.message.text}")
    try:
        user_message = update.message.text
        languages_key = context.user_data.get('current_languages')
        languages_data = context.user_data.get('languages_data')

        if not languages_key or not languages_data:
            await update.message.reply_text(
                f"Произошла ошибка: язык перевода не выбран. Используйте /translate для начала {languages_key} {languages_data}"
            )
            return SELECTION_LANGUAGE

        # Показываем индикатор "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        #Отправляем сообщение о том , что обрабатываем запрос
        processing_msg = await update.message.reply_text(
            f"{languages_data['emoji']} {languages_data['name']} переводит..."
        )

        languages_response = await get_personality_response(user_message,languages_data['prompt'])

        #Создаем кнопки
        keyboard = [
            # [InlineKeyboardButton('Продолжить диалог', callback_data="continue_chat")],
            [InlineKeyboardButton('Выбрать другой язык', callback_data="change_languages")],
            [InlineKeyboardButton('Закончить', callback_data="finish_translate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        #Удаляем сообщение обработки и отправляем ответ.
        await processing_msg.delete()
        await update.message.reply_text(
            f"{languages_data['emoji']} {languages_data['name']} отвечает: {languages_response}",
            parse_mode = 'HTML',
            reply_markup=reply_markup
        )

        return CHATING_WITH_TRANSLATOR
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения для переводчика {e}")
        await update.message.reply_text(
            "Произошла ошибка при обработке сообщения. Попробуйте еще раз"
        )
        return  -1
    
async def handle_languages_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок в диалоге с переводчиком"""
    query = update.callback_query
    logger.info(f"Получен callback в languages: {query.data}")
    await query.answer()

    if query.data == "continue_translate":
        languages_data = context.user_data.get("languages_data")
        if languages_data:
            pass # Заглушка на перезапуск диалога.
            logger.info("Здесь продолжение диалога с переводчиком")
        return CHATING_WITH_TRANSLATOR

    elif query.data == "change_languages":
        context.user_data.pop('current_languages', None)
        context.user_data.pop('languages_data', None)
        await translate_start(update,context)
        return SELECTION_LANGUAGE

    elif query.data == "finish_translate":
        # Очищаем личности
        context.user_data.clear()
        context.user_data.pop('current_languages',None)
        context.user_data.pop('languages_data',None)
        await basic.start(update, context)
        return  ConversationHandler.END

    return CHATING_WITH_TRANSLATOR