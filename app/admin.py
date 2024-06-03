import os
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
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
    if await is_admin(message.from_user.id):
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
    if await is_admin(message.from_user.id):
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        user_list = 'Список пользователей ЭнергоБота\n'
        for user in users:
            user_list += " | ".join(f"<code>{col}</code>" for col in user) + "\n"
        await message.answer(user_list, parse_mode=ParseMode.HTML)
    else:
        await message.reply('У вас нет доступа к этой команде!')

@admin.message(F.text == 'Показать пользователей')
async def cmd_show_users_text(message: Message):
    await cmd_show_users(message)


async def is_admin(user_id):
    cursor.execute("SELECT user_type FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if result and result[0] == 'admin':
        return True
    else:
        return False


@admin.message(F.text == 'Изменить тип пользователя')
async def cmd_edit_text(message: Message):
    await message.reply('Введите команду в формате /edit <id пользователя> <тип пользователя>\n'
                        'Администратор - admin \n'
                        'Студент - student \n'
                        'Преподаватель - teacher \n'
                        'Гость - guest')


@admin.message(Command('edit'))
async def cmd_edit(message: Message):
    if await is_admin(message.from_user.id):
        # Разбираем аргументы команды
        args = message.text.split()[1:]
        if len(args) == 2:
            user_id = args[0]
            new_user_type = args[1]

            # Проверяем, что пользователь не пытается изменить свой тип
            if user_id == message.from_user.id:
                await message.reply("Вы не можете изменить свой тип пользователя!")
                return

            valid_user_types = ['guest', 'student', 'teacher', 'admin']
            if new_user_type not in valid_user_types:
                await message.reply("Недопустимый тип пользователя. Используйте: guest, student, teacher, admin")
                return

            # Проверяем, что пользователь с указанным ID существует
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                await message.reply("Такого ID пользователя не найдено. Попробуйте еще раз.")
                return

            # Обновляем тип пользователя в базе данных
            cursor.execute("UPDATE users SET user_type = ? WHERE user_id = ?", (new_user_type, user_id))
            conn.commit()

            # Отправляем сообщение об успешном изменении
            await message.reply(f"Тип пользователя с ID {user_id} был изменен на {new_user_type}.")
        else:
            await message.reply("Неверный формат команды. Используйте: /edit <user_id> <user_type>")
    else:
        await message.reply("У вас нет прав для использования этой команды!")


@admin.message(F.text == 'Удалить пользователя')
async def cmd_del_text(message: Message):
    await message.reply(f'Чтобы удалить пользователя, напишите следующее: <b>/del_user (id пользователя)</b>',
                        parse_mode=ParseMode.HTML)


@admin.message(Command('del'))
async def cmd_del(message: Message):
    # Проверяем, является ли пользователь администратором
    if await is_admin(message.from_user.id):
        args = message.text.split()[1:]  # Получаем аргументы команды, исключая саму команду
        if len(args) != 1:
            await message.answer("Неверный формат команды. Используйте: /del_user <id>")
            return

        del_user_id = int(args[0])

        if del_user_id == message.from_user.id:
            await message.answer("Вы не можете удалить свой собственный ID.")
            return

        # Проверяем существование пользователя с указанным del_user_id
        cursor.execute("SELECT 1 FROM users WHERE user_id=?", (del_user_id,))
        existing_user = cursor.fetchone()
        if not existing_user:
            await message.answer(f"Пользователь с ID {del_user_id} не найден в базе данных.")
            return

        # Удаляем пользователя из базы данных
        cursor.execute("DELETE FROM users WHERE user_id=?", (del_user_id,))
        conn.commit()
        await message.answer(f"Пользователь с ID {del_user_id} успешно удален из базы данных.")
    else:
        await message.reply('У вас нет прав использовать данную команду!')


