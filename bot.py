import logging
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from handlers import basic, random_fact, chatgpt_interface, personality_chat

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

        # Обработка кнопки `personality`
        application.add_handler(CommandHandler("personality", personality_chat.talk_command))

        #Пеход в режим GPT
        gpt_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("gpt", chatgpt_interface.gpt_command),
                CallbackQueryHandler(chatgpt_interface.gpt_command, pattern="^gpt_interface$")],
            states={
                chatgpt_interface.WAITING_FOR_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_interface.handle_gpt_message),
                    CallbackQueryHandler(chatgpt_interface.finish_gpt, pattern="^(gpt_finish|main_menu)"),
                    CallbackQueryHandler(chatgpt_interface.continue_gpt, pattern="^gpt_continue")
                ],
            },
            fallbacks=[
                CommandHandler("start", basic.start),
                CallbackQueryHandler(basic.menu_callback, pattern="^(gpt_finish|main_menu)")
            ],
            # per_message=False
        )

        #Пеход в режим Personality
        personality_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(personality_chat.talk_start, pattern="^talk_interface$"),
                CommandHandler("talk", personality_chat.talk_start)
            ],
            states={
                personality_chat.SELECTION_PERSONALITY: [
                    CallbackQueryHandler(personality_chat.handle_personality_callback,
                                         pattern="^(continue_chat|finish_talk|change_personality)$"),
                    CallbackQueryHandler(personality_chat.personality_selected, pattern="^personality_.*")
                ],
                personality_chat.CHATING_WITH_PERSONALITY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, personality_chat.handle_personality_message),
                    CallbackQueryHandler(personality_chat.handle_personality_callback,
                                         pattern="^(continue_chat|finish_talk|change_personality)$")
                ],
            },
            fallbacks=[
                CommandHandler("start", basic.start),
                CallbackQueryHandler(basic.menu_callback, pattern="^main_menu")
            ]
        )

        # Обработка кнопки `personality`
        application.add_handler(personality_conversation)

        # Обработка кнопки `gpt`
        application.add_handler(gpt_conversation)

        # Обработка кнопки `Рандомный факт - query.data = random_fact -> random_fact.random_fact_callback`
        application.add_handler(CallbackQueryHandler(random_fact.random_fact_callback, pattern="^random_"))

        # Обработка команды `random`
        application.add_handler(CommandHandler("random", random_fact.random_fact))

        # Обработка команды `gpt`
        application.add_handler(CommandHandler("gpt", chatgpt_interface.gpt_command))

        # Обработчик кнопок "МЕНЮ"
        application.add_handler(CallbackQueryHandler(basic.menu_callback))

        # Запуск обработчика событий

        application.run_polling()

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)

if __name__ == '__main__':
        main()
