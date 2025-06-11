import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

# Подключаем переменной из окружения ".env"
load_dotenv()

CHATGPT_TOKEN = os.getenv("CHATGPT_TOKEN")
if not CHATGPT_TOKEN:
    raise ValueError("Введите токен в .env")
else:
    logger.info("GPT_TOKEN загружен !")


client = AsyncOpenAI(api_key=CHATGPT_TOKEN)

async def get_random_fact():
    """Получить случайный факт от ChatGPT"""
    logger.info("CHATGPT - get_random_fact")
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты помощник, который рассказывает интересные и познавательные факты. Отвечай на русском языке."
                },
                {
                    "role": "user",
                    "content": "Расскажи интересный случайный факт из любой области знаний. Факт должен быть познавательным, удивительным и не слишком длинным (максимум 3-4 предложения)."
                }
            ],
            max_tokens=200,
            temperature=0.8
        )

        fact = response.choices[0].message.content.strip()
        logger.info("Факт успешно получен от OpenAI")
        return fact

    except Exception as e:
        logger.error(f"Ошибка при получении факта от OpenAI: {e}")
        return "🤔 К сожалению, не удалось получить факт в данный момент. Попробуйте позже!"

async def get_chatgpt_response(messages :list):
    """Получение ответа на запрос пользоватля"""
    logger.info(f"Запрос к OpenAI {messages}")
    try:
        # Проверяем, что все сообщения имеют строковый content
        for msg in messages:
            if not isinstance(msg["content"], str):
                logger.error(f"Некорректный формат content в сообщении: {msg}")
                raise ValueError(f"Content должен быть строкой, получено: {msg['content']}")

        full_messages = [
                            {
                                "role": "system",
                                "content": "Ты полезный помощник. Отвечай на русском языке, будь дружелюбным и информативным. Если не знаешь ответ, честно об этом скажи."
                            }
                        ] + messages  # Добавляем историю к системному промпту

        logger.info(f"Полный список сообщений, отправляемый в OpenAI: {full_messages}")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=full_messages,
            max_tokens=1000,
            temperature=0.7
        )

        answer = response.choices[0].message.content
        logger.info(f"Ответ успешно получен от OpenAI {answer}")
        return answer

    except Exception as e:
        logger.error(f"Ошибка при получении ответа от OpenAI: {e}")
        return "😔 Извините, произошла ошибка при обращении к ChatGPT. Попробуйте позже!"

async def get_personality_response(user_message, personality_prompt: str):
    """Получить ответ от чата GPT"""
    try:
        respnse = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": personality_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=80,
            temperature=0.8
        )

        answer = respnse.choices[0].message.content.strip()
        logger.info("Персонифицированный ответ успешно получен от OpenAI")
        return answer

    except Exception as e:
        logger.error(f"Ошибка при получении персонифицированного ответа: {e}")
        return "😔 Извините, произошла ошибка при обращении к ChatGPT. Попробуйте позже!"