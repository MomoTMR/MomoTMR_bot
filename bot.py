import logging
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers import basic, random_fact

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

        # Обработка кнопки `start`
        start_handler = CommandHandler('start', basic.start)
        application.add_handler(start_handler)

        # Обработка кнопки `random`
        application.add_handler(CallbackQueryHandler(random_fact.random_fact_callback, pattern="^random_"))

        # Обработчик кнопок "МЕНЮ"
        application.add_handler(CallbackQueryHandler(basic.menu_callback))

        # Запуск обработчика событий
        application.run_polling()
    except Exception as e:
        logger.error('Ошибка при запуске', e)

if __name__ == '__main__':
    main()
