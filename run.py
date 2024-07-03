import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from config import ADMIN_ID
from config import TOKEN
from handlers.admin import admin
from handlers.handlers import hand
from handlers.send_files import file
from handlers.student import std
from handlers.teacher import teach


async def main():
    load_dotenv()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(hand, admin, std, teach, file)
    await bot.send_message(ADMIN_ID, 'Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)    
    try:
        print('Бот запущен')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
