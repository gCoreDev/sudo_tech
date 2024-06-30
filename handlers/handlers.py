import asyncio
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import ChatAction
import handlers.keyboards as kb
import openpyxl
from handlers.create_data_base import (cur_users, conn_users)
from config import DATA_DIR

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
    conn_users.close()


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
