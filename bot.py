import logging
import os
from conversation import *
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

# Подулючаем переменную из окружения ".env"
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

#Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Проверка статуса диалога
def is_in_conversation(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.user_data.get('conversation_active', False)

# Определяем типы сосотяний для converstaion
GENDER, PHOTO, LOCATION, BIO = range(4)

# Срабатывает каждый раз когда бот получает команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start mode")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я бот, пожалуйста поговори со мной!"
    )

# Эхо-ответ на текстовые сообщения
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Echo status")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text
    )

# Преобразование текста в верхний регистр
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("CAPS STATUS")
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_caps
    )

# Обработка неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Неизвестная команда")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Сорян, я не знаю таокй команды."
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)

    #Запуск Conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("conv", conv)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
                MessageHandler(filters.ALL, handle_wrong_input_location),  # <- фильтр на все остальные случаи
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(conv_handler)
    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    application.add_handler(echo_handler)
    application.add_handler(unknown_handler)



    application.run_polling()