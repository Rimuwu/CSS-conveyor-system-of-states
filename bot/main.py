from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from os import getenv
from dotenv import load_dotenv

load_dotenv()

botik = Bot(getenv('BOT_TOKEN'))
STORAGE = MemoryStorage()

dp = Dispatcher(storage=STORAGE)
css_router = Router()
test_router = Router()

def run():
    import interface.handlers
    import bot.handlers

    print("Бот запущен")

    dp.include_router(css_router)
    dp.include_router(test_router)
    asyncio.run(dp.start_polling(botik))