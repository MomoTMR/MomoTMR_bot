import logging
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from handlers import basic, random_fact, chatgpt_interface

#Включаем логирование.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Подулючаем переменной из окружения ".env"
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Введите токен в .env")
else:
    logger.info("TELEGRAM_TOKEN load complite")

def main():
    try:
        # Инициализация TELEGRAM_TOKEN
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Обработка команды `start`
        start_handler = CommandHandler('start', basic.start)
        application.add_handler(start_handler)

        # Обработка команды `random`
        application.add_handler(CommandHandler("random", random_fact.random_fact))

        # Обработка команды `gpt`
        application.add_handler(CommandHandler("gpt", chatgpt_interface.gpt_command))

        # Обработка кнопки `gpt`
        application.add_handler(CommandHandler("gpt", chatgpt_interface.gpt_command))

        gpt_conversation = ConversationHandler(
            entry_points=[CallbackQueryHandler(chatgpt_interface.gpt_start, pattern="^gpt_interface$")],
            states={
                chatgpt_interface.WAITING_FOR_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_interface.handle_gpt_message)
                ],
            },
            fallbacks=[
                CommandHandler("start", basic.start),
                CallbackQueryHandler(basic.menu_callback, pattern="^(gpt_finish|main_menu)$")
            ],
            #per_message=True
        )

        application.add_handler(gpt_conversation)

        # Обработка кнопки `random`
        application.add_handler(CallbackQueryHandler(random_fact.random_fact_callback, pattern="^random_"))

        # Обработчик кнопок "МЕНЮ"
        application.add_handler(CallbackQueryHandler(basic.menu_callback))

        # Запуск обработчика событий
        application.run_polling()
    except Exception as e:
        logger.error(f'Ошибка при запуске, {e}')

if __name__ == '__main__':
    main()
