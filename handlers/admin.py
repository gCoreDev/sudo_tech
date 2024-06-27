from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
import handlers.keyboards as kb
import sqlite3

from config import TOKEN, bot, DATA_DIR

admin = Router()

conn = sqlite3.connect(DATA_DIR / 'data_base/users.db')
cur = conn.cursor()


@admin.message(F.text == 'Личный кабинет')
async def per_acc_adm(message: Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_username = message.from_user.username
    cur.execute('SELECT user_type FROM users WHERE user_id=?', (user_id,))
    user = cur.fetchone()
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
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    user_list = 'Список пользователей\n'
    for user in users:
        user_list += ' | '.join(f'`{col}`' for col in user) + "\n"
    await message.answer(user_list, parse_mode=ParseMode.MARKDOWN)


async def is_admin(user_id):
    cur.execute("SELECT user_type FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
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
            cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            if not cur.fetchone():
                await message.reply(f"‼️Пользователь с ID {user_id} не найден в базе данных.")
                return

            # Обновляем тип пользователя в базе данных
            cur.execute("UPDATE users SET user_type = ? WHERE user_id = ?", (new_user_type, user_id))
            conn.commit()

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
    cur.execute("SELECT user_type FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()
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
    cur.execute("SELECT 1 FROM users WHERE user_id=?", (del_user_id,))
    existing_user = cur.fetchone()
    if not existing_user:
        await message.answer(f"‼️Пользователь с ID {del_user_id} не найден в базе данных.")
        return

    # Удаляем пользователя из базы данных
    cur.execute("DELETE FROM users WHERE user_id=?", (del_user_id,))
    conn.commit()
    await message.answer(f"✅ Пользователь с ID {del_user_id} успешно удален из базы данных.")


@admin.message(F.text == 'Показать пользователей')
async def cmd_text_users(message: Message):
    await cmd_users(message)


@admin.message(F.text == 'Изменить тип пользователя')
async def cmd_text_edit(message: Message):
    await message.reply('Чтобы изменить тип учетной записи пользователя, напишите следующую команду \n'
                        '/edit (id пользователя) (тип пользователя)')


@admin.message(F.text == 'Удалить пользователя')
async def cmd_text_del(message: Message):
    await message.reply('Чтобы удалить запись пользователя, напишите следующую команду \n'
                        '/del (id пользователя)')


class SendMessage(StatesGroup):
    awaiting_message = State()


def get_all_user_ids():
    cur.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cur.fetchall()]
    return user_ids


async def send_message_to_all(message: Message):
    user_ids = get_all_user_ids()
    for user_id in user_ids:
        await bot.send_message(user_id, f'<b>Сообщение от админа</b>\n{message.text}', parse_mode=ParseMode.HTML)


@admin.message(F.text == 'Сделать рассылку')
async def send_message(message: Message, state: FSMContext):
    if await is_admin(message.from_user.id):
        await state.update_data(awaiting_message=message.text)
        await state.set_state(SendMessage.awaiting_message)
        await message.reply('Напишите ваше сообщение для всех пользователей')
    else:
        await message.answer('У вас недостаточно прав!')


@admin.message(SendMessage.awaiting_message)
async def text_send_message(message: Message, state: FSMContext):
    if message.text.startswith('Сделать рассылку'):
        return
    await send_message_to_all(message)
    await message.answer('Сообщение успешно отправлено')
    await state.clear()


@admin.message(F.text == 'Расписание')
async def week_plan(message: Message):
    await message.answer('Выберите действие над расписанием', reply_markup=kb.week_plan)


@admin.callback_query(F.data == 'upload_week_plan')
async def data_upload_week_plan(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Чтобы загрузить расписание, отправьте мне файл в формате .xlxs')


@admin.callback_query(F.data == 'check_week_plan')
async def data_check_week_plan(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('<b>Расписание на понедельник:</b>\n'
                                  '1) Математика - Николай И.Н. 301 каб \n'
                                  '2) Русский язык - Иванова А.М. 105 каб.\n'
                                  '3) Информатика - Лебедев Н.О. 224 каб.\n'
                                  '4) Физкультура - Елисеев А.П. 111 каб.',
                                  parse_mode=ParseMode.HTML)


@admin.callback_query(F.data == 'del_week_plan')
async def data_del_week_plan(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Введите команду /del week_plan')
