import os
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import app.keyboards as kb
import sqlite3

load_dotenv()

admin = Router()

ADMIN_ID = int(os.getenv('ADMIN_ID'))
STUDENT_ID = int(os.getenv('STUDENT_ID'))
TEACHER_ID = int(os.getenv('TEACHER_ID'))

conn = sqlite3.connect('app/docs/data_base/users.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                user_fullname TEXT,
                user_name TEXT,
                user_type TEXT
                )''')
conn.commit()

# Тут если нужно вручную добавляем ID пользователей
# cursor.execute('''INSERT INTO users (user_id, user_fullname, user_name, user_type)
#                 VALUES ('7355741014','Николай Иванович','enegry200', 'teacher')
#                 ''')
# conn.commit()
# conn.close()

# Если нужно кого-то удалить из базы
# cursor.execute("DELETE FROM users WHERE user_id = '529088802'")
# conn.commit()
# conn.close()

@admin.message(Command('admin'))
async def cmd_admin(message: Message):
    if ADMIN_ID == message.from_user.id:
        await message.answer('Вы в админ панели!', reply_markup=kb.admin_panel())
    else:
        await message.answer('В доступе отказано!')


@admin.message(F.text == 'Личный кабинет')
async def personal_account(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT user_type FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        user_type = user[0]
        if user_type == 'admin':
            await message.answer('Вы в админ панели',
                                 reply_markup=kb.admin_panel())
        elif user_type == 'student':
            await message.answer(f'Добро пожаловать,'
                                 f' {message.from_user.full_name}, студент!',
                                 reply_markup=kb.std_panel())
        elif user_type == 'teacher':
            await message.answer(f'Добро пожаловать преподаватель,'
                                 f' <b>{message.from_user.full_name}!</b>',
                                 parse_mode=ParseMode('HTML'),
                                 reply_markup=kb.teacher_panel())
        else:
            await message.answer(f'К сожалению, вы не можете воспользоваться личным кабинетом')
    else:
        await message.answer(f'Дорогой гость, {message.from_user.full_name}, вы находитесь в главном меню!')
        user_fullname = message.from_user.full_name
        user_name = message.from_user.username
        cursor.execute("INSERT INTO users (user_id, user_fullname, user_name, user_type) VALUES (?, ?, ?, ?)",
                       (user_id, user_fullname, user_name, 'guest'))
        conn.commit()

# class Broadcast(StatesGroup):
#     wait_broadcast_message = State()
#
#
# @admin.message(F.text == 'Сделать рассылку')
# async def cmd_broadcast(message: Message, state: FSMContext):
#     await state.update_data(wait_broadcast_message=message.text)
#     await state.set_state(Broadcast.wait_broadcast_message)
#     await message.answer('Напишите сообщение для рассылки - оно будет отправлено '
#                          'всем пользователям')
#
#
# @admin.message(Broadcast.wait_broadcast_message)
# async def send_broadcast(message: Message, state: FSMContext):
#     if message.text.startswith('Сделать рассылку'):
#         return
#     await send_broadcast_all(message)
#     await message.answer('Сообщение успешно отправлено')
#     await state.clear()


@admin.message(Command('show_users'))
async def cmd_show_users(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT user_type FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if user:
        user_type = user[0]
        if user_type == 'admin':
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            user_list = 'Список пользователей ЭнергоБота\n'
            for user in users:
                user_list += " | ".join(str(col) for col in user) + "\n"
            await message.answer(user_list)
        else:
            await message.reply('У вас нет доступа к этой команде!')
    else:
        await message.answer('Если вы видите это сообщение, то по какой-то причине - вас не в базе')

@admin.message(F.text == 'Показать пользователей')
async def cmd_show_users_text(message: Message):
    await cmd_show_users(message)
