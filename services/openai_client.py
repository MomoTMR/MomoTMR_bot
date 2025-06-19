"""
Клиент для работы с OpenAI API.

Этот модуль предоставляет асинхронные функции для взаимодействия с OpenAI ChatGPT API.
Поддерживает следующие функции:
- Генерация случайных фактов
- Общение с ChatGPT в режиме диалога
- Персонифицированные ответы с различными личностями

Требует настройки переменной окружения CHATGPT_TOKEN с действующим API ключом OpenAI.
"""

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
    """
    Получить случайный факт от ChatGPT.

    Генерирует интересный и познавательный факт из любой области знаний
    с использованием OpenAI API.

    Returns:
        str: Случайный факт или сообщение об ошибке
    """
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

async def get_chatgpt_response(messages: list):
    """
    Получение ответа ChatGPT на запрос пользователя.

    Отправляет список сообщений в OpenAI API и получает ответ от ChatGPT.
    Поддерживает контекст диалога через историю сообщений.

    Args:
        messages (list): Список сообщений в формате [{"role": "user/assistant", "content": "текст"}]

    Returns:
        str: Ответ от ChatGPT или сообщение об ошибке
    """
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
    """
    Получить персонифицированный ответ от ChatGPT.

    Генерирует ответ от ChatGPT, используя специальный промпт для имитации
    определенной личности или персонажа.

    Args:
        user_message (str): Сообщение от пользователя
        personality_prompt (str): Промпт с описанием личности для системной роли

    Returns:
        str: Персонифицированный ответ от ChatGPT или сообщение об ошибке
    """
    try:
        response = await client.chat.completions.create(
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

        answer = response.choices[0].message.content.strip()
        logger.info("Персонифицированный ответ успешно получен от OpenAI")
        return answer

    except Exception as e:
        logger.error(f"Ошибка при получении персонифицированного ответа: {e}")
        return "😔 Извините, произошла ошибка при обращении к ChatGPT. Попробуйте позже!"
