import requests
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
import handlers.keyboards as kb
from handlers.create_data_base import (cur_users, conn_users)
from config import bot

admin = Router()


@admin.message(F.text == 'Личный кабинет 👤')
async def per_acc_adm(message: Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    cur_users.execute('SELECT user_type FROM users WHERE user_id=?', (user_id,))
    user = cur_users.fetchone()
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
            await message.answer('⚠️ У вас нет доступа к личному кабинету! Если вы студент или преподаватель колледжа,'
                                 'обратитесь к своему куратору')


@admin.message(Command('users'))
async def cmd_users(message: Message):
    cur_users.execute('SELECT * FROM users')
    users = cur_users.fetchall()
    user_list = 'Список пользователей\n'
    for user in users:
        user_list += ' | '.join(f'`{col}`' for col in user) + "\n"
    await message.answer(user_list, parse_mode=ParseMode.MARKDOWN)


async def is_admin(user_id):
    cur_users.execute("SELECT user_type FROM users WHERE user_id = ?", (user_id,))
    result = cur_users.fetchone()
    if result and result[0] == 'admin':
        return True
    else:
        return False


@admin.message(Command('edit'))
async def cmd_edit(message: Message):
    if await is_admin(message.from_user.id):
        # Разбираем аргументы команды
        args = message.text.split()[1:]
        if len(args) == 2:
            try:
                user_id = int(args[0])
            except ValueError:
                await message.reply("‼️Неверный формат ID пользователя. ID должен быть целым числом.")
                return

            new_user_type = args[1]

            # Проверяем, что пользователь не пытается изменить свой тип
            if user_id == message.from_user.id:
                await message.reply("‼️Вы не можете изменить свой тип пользователя!")
                return

            # Проверяем, что пользователь существует в базе данных
            cur_users.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            if not cur_users.fetchone():
                await message.reply(f"‼️Пользователь с ID {user_id} не найден в базе данных.")
                return

            # Обновляем тип пользователя в базе данных
            cur_users.execute("UPDATE users SET user_type = ? WHERE user_id = ?", (new_user_type, user_id))
            conn_users.commit()

            valid_user_types = ['guest', 'student', 'teacher', 'admin']
            if new_user_type not in valid_user_types:
                await message.reply("‼️Недопустимый тип пользователя. Используйте: guest, student, teacher, admin")
                return

            # Отправляем сообщение об успешном изменении
            await message.reply(f"✅ Тип пользователя с ID {user_id} был изменен на {new_user_type}.")
        else:
            await message.reply("Неверный формат команды. Используйте: /edit_user <user_id> <user_type>")
    else:
        await message.reply("⚠️ У вас нет прав для использования этой команды ")


@admin.message(Command('del'))
async def cmd_del(message: Message):
    user_id = message.from_user.id
    cur_users.execute("SELECT user_type FROM users WHERE user_id=?", (user_id,))
    user = cur_users.fetchone()
    if not user or user[0] != 'admin':
        await message.answer("⚠️ У вас нет прав для использования этой команды!")
        return

    args = message.text.split()[1:]  # Получаем аргументы команды, исключая саму команду
    if len(args) != 1:
        await message.answer("‼️Неверный формат команды. Используйте: /del_user (id)")
        return

    del_user_id = int(args[0])

    if del_user_id == user_id:
        await message.answer("‼️Вы не можете удалить свой собственный ID.")
        return

    # Проверяем существование пользователя с указанным del_user_id
    cur_users.execute("SELECT 1 FROM users WHERE user_id=?", (del_user_id,))
    existing_user = cur_users.fetchone()
    if not existing_user:
        await message.answer(f"‼️Пользователь с ID {del_user_id} не найден в базе данных.")
        return

    # Удаляем пользователя из базы данных
    cur_users.execute("DELETE FROM users WHERE user_id=?", (del_user_id,))
    conn_users.commit()
    await message.answer(f"✅ Пользователь с ID {del_user_id} успешно удален из базы данных.")


@admin.message(F.text == 'Показать пользователей 👤')
async def cmd_text_users(message: Message):
    await cmd_users(message)


@admin.message(F.text == 'Изменить тип пользователя ✏️')
async def cmd_text_edit(message: Message):
    await message.reply('Чтобы изменить тип учетной записи пользователя, напишите следующую команду \n'
                        '/edit (id пользователя) (тип пользователя)')


@admin.message(F.text == 'Удалить пользователя ✖️')
async def cmd_text_del(message: Message):
    await message.reply('Чтобы удалить запись пользователя, напишите следующую команду \n'
                        '/del (id пользователя)')


class SendMessage(StatesGroup):
    awaiting_message = State()


def get_all_user_ids():
    cur_users.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cur_users.fetchall()]
    return user_ids


async def send_message_to_all(message: Message):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        await bot.send_message(user_id, f'<b>Сообщение от админа</b>\n{message.text}', parse_mode=ParseMode.HTML)


@admin.message(F.text == 'Сделать рассылку 📢')
async def send_message(message: Message, state: FSMContext):
    if await is_admin(message.from_user.id):
        await state.update_data(awaiting_message=message.text)
        await state.set_state(SendMessage.awaiting_message)
        await message.reply('Напишите ваше сообщение для всех пользователей')
    else:
        await message.answer('У вас недостаточно прав!')


@admin.message(SendMessage.awaiting_message)
async def text_send_message(message: Message, state: FSMContext):
    if message.text.startswith('Сделать рассылку 📢'):
        return
    await send_message_to_all(message)
    await message.answer('Сообщение успешно отправлено')
    await state.clear()


@admin.message(F.text == 'Расписание 🗓')
async def week_plan(message: Message):
    await message.answer('Выберите действие над расписанием', reply_markup=kb.week_plan)


@admin.callback_query(F.data == 'upload_week_plan')
async def data_upload_week_plan(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Чтобы загрузить расписание, отправьте мне файл в формате .xlxs')


@admin.callback_query(F.data == 'check_week_plan')
async def data_check_week_plan(callback: CallbackQuery):
    await callback.answer('')
    schedule = dict(Понедельник=[
        '1) Математика - Николай И.Н. 301 каб',
        '2) Русский язык - Иванова А.М. 105 каб.',
        '3) Информатика - Лебедев Н.О. 224 каб.',
        '4) Физкультура - Елисеев А.П. 111 каб.'
    ], Вторник=[
        '1) История - Петров С.В. 201 каб.',
        '2) Литература - Сидорова Т.Ю. 105 каб.',
        '3) Физика - Смирнов А.И. 302 каб.',
        '4) Английский язык - Кузнецова М.Н. 107 каб.'
    ], Среда=[
        '1) Химия - Иванов П.П. 303 каб.',
        '2) Биология - Сергеева Е.Д. 304 каб.',
        '3) Обществознание - Соколов Д.В. 202 каб.',
        '4) Технология - Петрова А.С. 106 каб.'
    ], Четверг=[
        '1) Алгебра - Николай И.Н. 301 каб.',
        '2) Геометрия - Николай И.Н. 301 каб.',
        '3) Физкультура - Елисеев А.П. 111 каб.',
        '4) ОБЖ - Смирнов А.И. 302 каб.'
    ], Пятница=[
        '1) Русский язык - Иванова А.М. 105 каб.',
        '2) Литература - Сидорова Т.Ю. 105 каб.',
        '3) Информатика - Лебедев Н.О. 224 каб.',
        '4) Английский язык - Кузнецова М.Н. 107 каб.'
    ])

    schedule_text = '<b>Расписание на неделю:</b>\n\n'
    for day, lessons in schedule.items():
        schedule_text += f'<b>{day}:</b>\n'
        for lesson in lessons:
            schedule_text += f'- {lesson}\n'
        schedule_text += '\n'

    await callback.message.answer(schedule_text, parse_mode=ParseMode.HTML)


@admin.callback_query(F.data == 'del_week_plan')
async def data_del_week_plan(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Введите команду /del week_plan')




