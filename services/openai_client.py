import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

# Подулючаем переменной из окружения ".env"
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