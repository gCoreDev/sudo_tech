import logging
import os
import asyncio

from aiogram import Bot, Dispatcher

from dotenv import load_dotenv

from app.handlers import hand
from app.admin import admin
from app.student import std
from app.teacher import teach


ADMIN_ID = int(os.getenv('ADMIN_ID'))


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_routers(hand, admin, std, teach)
    await bot.send_message(ADMIN_ID, 'Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)    
    try:
        print('Бот запущен')
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
