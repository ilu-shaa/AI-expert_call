# main.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.config import TG_TOKEN
from app.handlers import router as main_router
from app.new_voice_handler import router as voice_router

async def main():
    # Инициализация бота с нужным parse_mode
    bot = Bot(token=TG_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Подключаем маршрутизаторы
    dp.include_router(main_router)
    dp.include_router(voice_router)

    print("🚀 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
