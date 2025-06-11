import asyncio
from aiogram import Bot, Dispatcher

from handlers import router
from config import TG_TOKEN

bot = Bot(token = TG_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())