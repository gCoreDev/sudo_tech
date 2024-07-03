import asyncio

import requests
from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import ChatAction
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import handlers.keyboards as kb
import openpyxl
from config import DATA_DIR, WEATHER, bot
from handlers.create_data_base import conn_users, cur_users

hand = Router()


@hand.message(CommandStart())
async def cmd_start(message: Message):
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(1)
    await message.answer_photo(photo='https://lh3.googleusercontent.com/'
                               'p/AF1QipM8MkG4sv0a2Fk-hQYESG-H3A5rmjC9Y68GLEhi=w600-k')
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username

    # Проверяем, существует ли пользователь в базе данных
    cur_users.execute("SELECT * FROM users WHERE user_id = ?",
                      (user_id,))
    if cur_users.fetchone() is None:
        # Если пользователь не существует, добавляем его в базу данных
        cur_users.execute('INSERT INTO users (user_id, user_full_name, user_username, user_type)'
                          'VALUES (?, ?, ?, ?)',
                          (user_id, user_full_name, user_username, 'student'))
        conn_users.commit()
        await message.answer('Добро пожаловать гость Вы находитесь в главном меню', reply_markup=kb.main)
    else:
        # Если пользователь уже существует, отправляем сообщение о входе
        # await message.answer(f'Добро пожаловать {user_type} Вы находитесь в главном меню', reply_markup=kb.main)
        user_id = message.from_user.id
        cur_users.execute('SELECT user_type FROM users WHERE user_id=?',
                          (user_id,))
        user = cur_users.fetchone()
        if user:
            user_type = user[0]
            if user_type == 'admin':
                await message.answer(f'Добро пожаловать, администратор {message.from_user.full_name},'
                                     f' Вы находитесь в главном меню', reply_markup=kb.main)
            elif user_type == 'student':
                await message.answer(f'Добро пожаловать, студент {message.from_user.full_name},'
                                     f' Вы находитесь в главном меню', reply_markup=kb.main)
            elif user_type == 'teacher':
                await message.answer(f'Добро пожаловать, преподаватель {message.from_user.full_name},'
                                     f' Вы находитесь в главном меню', reply_markup=kb.main)
            else:
                await message.answer(f'Добро пожаловать, гость, {message.from_user.full_name}'
                                     f' Вы находитесь в главном меню', reply_markup=kb.main)


@hand.message(Command('check_list'))
async def cmd_table(message: Message):
    book = openpyxl.open(DATA_DIR / "docs/data.xlsx", read_only=True)
    sheet = book.active

    output = ""

    for row in sheet.iter_rows(min_row=1, values_only=True):
        row_values = []
        for cell in row:
            if cell is not None and cell != "":
                row_values.append(str(cell))
        if row_values:
            output += "| " + " | ".join(row_values) + " |\n"

    if output:
        parts = [output[i:i + 2000] for i in range(0, len(output), 2000)]  # разбиваем строку
        # на части по
        # 2000 символов
        for part in parts:
            await message.answer("```\n" + part + "```")  # отправляем каждую часть отдельно
    else:
        await message.answer("Таблица пуста или не содержит заполненных ячеек.")


@hand.message(F.text == 'Назад 🔙')
async def cmd_start_back(message: Message):
    await cmd_start(message)


@hand.message(F.text == 'Узнать о боте 📖')
async def cmd_about(message: Message):
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(1)
    await message.reply(f'Приветствую, {message.from_user.full_name}, я '
                        f'ЭнергоБот, созданный для помощи между студентами и '
                        f'преподавателями. Я еще в разработке. Если вы '
                        f'студент или преподаватель, вы можете зайти в '
                        f'личный кабинет, однако если не выходит, '
                        f'обратитесь к вашему куратору.')


@hand.message(F.text == 'Сайт колледжа 💻')
async def cmd_site(message: Message):
    await message.answer_photo(photo='https://lh3.googleusercontent.com'
                                     '/p/AF1QipM8MkG4sv0a2Fk-hQYESG-H3A'
                                     '5rmjC9Y68GLEhi=w600-k')
    await message.answer('Сайт энергетического колледжа', reply_markup=kb.site)


@hand.message(F.text == 'Новости колледжа 📢')
async def cmd_group(message: Message):
    await message.answer_photo(photo='https://proverili.ru/uploads/media/'
                                     '5236/1.jpg')
    await message.answer('Канал колледжа', reply_markup=kb.group)


def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER}&units=metric"
    response = requests.get(url)
    return response.json()


async def send_daily_weather(bot: Bot):
    city = "Vladivostok"  # Замените на нужный город

    weather_data = get_current_weather(city)

    # Формирование сообщения с информацией о погоде
    weather_message = f"Доброе утро! Сегодняшняя погода в {city}:\n" \
                      f"Температура: {weather_data['main']['temp']}°C\n" \
                      f"Влажность: {weather_data['main']['humidity']}%\n" \
                      f"Скорость ветра: {weather_data['wind']['speed']} м/с"

    # Отправка сообщения всем пользователям бота
    user_ids = await get_all_user_ids()

    # Отправка сообщения всем пользователям
    for user_id in user_ids:
        await bot.send_message(chat_id=user_id, text=weather_message)


async def get_all_user_ids():
    cur_users.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cur_users.fetchall()]
    return user_ids


@hand.message(F.text == 'Погода 🌤')
async def text_weather(message: Message):
    city = "Vladivostok"  # Замените на нужный город

    try:
        weather_data = get_current_weather(city)

        # Формирование сообщения с информацией о погоде
        weather_message = f"Текущая погода в {city}:\n" \
                          f"Температура: {weather_data['main']['temp']}°C\n" \
                          f"Влажность: {weather_data['main']['humidity']}%\n" \
                          f"Скорость ветра: {weather_data['wind']['speed']} м/с"

        # Отправка сообщения пользователю
        await message.answer(weather_message)

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


scheduler = AsyncIOScheduler()
scheduler.add_job(send_daily_weather, "cron", hour=8, minute=0, args=[bot])
scheduler.start()
