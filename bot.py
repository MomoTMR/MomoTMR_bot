import logging
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from handlers import basic, random_fact, chatgpt_interface, personality_chat, quiz, translator_chat, voice_chat
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

from services import voice_recognition

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

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
    raise ValueError("Введите TELEGRAM_TOKEN токен в файле .env")
else:
    logger.debug("TELEGRAM_TOKEN loaded successfully")

def main():
    try:
        # Инициализация TELEGRAM_TOKEN
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Регистрация основных команд бота
        command_handlers = {
            'start': basic.start,
            'random': random_fact.random_fact,
            'gpt': chatgpt_interface.gpt_command,
            'personality': personality_chat.talk_command,
            'quiz': quiz.quiz_command,
            'translate':translator_chat.translate_command,
            'voice':voice_chat.start_voice_dialog
        }
        for command, handler_func in command_handlers.items():
            application.add_handler(CommandHandler(command, handler_func))

        # Обработка кнопки `Рандомный факт - query.data = random_fact -> random_fact.random_fact_callback`
        application.add_handler(CallbackQueryHandler(random_fact.random_fact_callback, pattern="^random_"))

        #Пеход в режим GPT
        gpt_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("gpt", chatgpt_interface.gpt_command),
                CallbackQueryHandler(chatgpt_interface.gpt_command, pattern="^gpt_interface$")],
            states={
                chatgpt_interface.WAITING_FOR_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_interface.handle_gpt_message),
                    CallbackQueryHandler(chatgpt_interface.finish_gpt, pattern="^(gpt_finish$|main_menu$)"),
                    CallbackQueryHandler(chatgpt_interface.continue_gpt, pattern="^gpt_continue")
                ],
            },
            fallbacks=[
                CommandHandler("start", basic.start),
                CallbackQueryHandler(basic.menu_callback, pattern="^(gpt_finish$|main_menu$)")
            ]
        )

        #Пеход в режим Personality
        personality_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("talk", personality_chat.talk_command),
                CallbackQueryHandler(personality_chat.talk_start, pattern="^talk_interface$")
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
                CallbackQueryHandler(basic.menu_callback, pattern="^(gpt_finish$|main_menu$)")
            ]
        )

        # Переход в режим Quiz
        quiz_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("quiz", quiz.quiz_command),
                CallbackQueryHandler(quiz.quiz_start, pattern="^quiz_interface$")
            ],
            states={
                quiz.SELECTING_TOPIC: [
                    CallbackQueryHandler(quiz.topic_selected, pattern="^quiz_topic_")
                ],
                quiz.ANSWERING_QUESTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, quiz.handle_quiz_answer),
                    CallbackQueryHandler(quiz.handle_quiz_callback,
                                         pattern="^quiz_continue_"),
                    CallbackQueryHandler(quiz.handle_quiz_callback,
                                         pattern="^quiz_change_topic$"),
                    CallbackQueryHandler(quiz.handle_quiz_callback,
                                         pattern="^quiz_finish$")
                ],
            },
            fallbacks=[
                CommandHandler("start", basic.start),
                CallbackQueryHandler(quiz.handle_quiz_callback, pattern="^quiz_finish$")
            ]
        )

        # Переход в режим Translate
        translator_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("translate", translator_chat.translate_command),
                CallbackQueryHandler(translator_chat.translate_start, pattern="^translate_interface$")
            ],
            states={
                translator_chat.SELECTION_LANGUAGE: [
                    CallbackQueryHandler(translator_chat.handle_languages_callback,
                                         pattern="^(continue_translate|finish_translate|change_languages)$"),
                    CallbackQueryHandler(translator_chat.languages_selected, pattern="^languages_.*")
                ],
                translator_chat.CHATING_WITH_TRANSLATOR: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, translator_chat.handle_languages_message),
                    CallbackQueryHandler(translator_chat.handle_languages_callback,
                                         pattern="^(continue_translate|finish_translate|change_languages)$")
                ],
            },
            fallbacks=[
                CommandHandler("start", basic.start),
                CallbackQueryHandler(basic.menu_callback, pattern="^(finish_translate|main_menu$)")
            ]
        )
        voice_conversation = ConversationHandler(
            entry_points=[
                CommandHandler("voice", voice_chat.start_voice_dialog),
                CallbackQueryHandler(voice_chat.start_voice_dialog, pattern="^start_voice_dialog$")
            ],
            states={
                voice_chat.VOICE_DIALOG: [
                    MessageHandler(filters.VOICE, voice_recognition.handle_voice),
                ]
            },
            fallbacks=[
                CommandHandler("start", basic.start),
                CallbackQueryHandler(voice_chat.voice_cancel, pattern="^(main_menu|voice_stop)$")
            ]
        )


        # Обработка кнопки `gpt`
        application.add_handler(gpt_conversation)

        # Обработка кнопки `personality`
        application.add_handler(personality_conversation)

        # Обработка кнопки `quiz`
        application.add_handler(quiz_conversation)

        # Обработка кнопки `translate`
        application.add_handler(translator_conversation)

        # Обработка кнопки `voice`
        application.add_handler(voice_conversation)

        # Обработчик кнопок "МЕНЮ"
        # application.add_handler(CallbackQueryHandler(basic.menu_callback))
        application.add_handler(CallbackQueryHandler(basic.menu_callback, pattern="^halt$"))

        # Запуск обработчика событий
        application.run_polling()

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)

if __name__ == '__main__':
        main()
