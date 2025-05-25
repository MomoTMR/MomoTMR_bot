from telegram import Bot
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def main():
    bot = Bot(TELEGRAM_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook удалён!")

if __name__ == '__main__':
    asyncio.run(main())