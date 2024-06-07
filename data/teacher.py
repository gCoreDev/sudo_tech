from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
import os
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
import data.keyboards as kb
import sqlite3

load_dotenv()

STUDENT_ID = int(os.getenv('STUDENT_ID'))
bot = Bot(token=os.getenv('TOKEN'))
ADMIN_ID = int(os.getenv('ADMIN_ID'))
TEACHER_ID = int(os.getenv('TEACHER_ID'))

teach = Router()
conn = sqlite3.connect('data/docs/data_base/users.db')
cursor = conn.cursor()


async def is_teacher(user_id):
	cursor.execute("SELECT user_type FROM users WHERE user_id=?", (user_id,))
	result = cursor.fetchone()
	if result and result[0] == 'teacher':
		return True
	else:
		return False


class StudentAnswer(StatesGroup):
	waiting_for_response = State()


async def send_message_to_student(message: Message):
	await bot.send_message(STUDENT_ID, f'<b>Сообщение от преподавателя,'
									f' {message.from_user.full_name}\n</b>'
									f' {message.text}',
									reply_markup=kb.st_answer,
									parse_mode=ParseMode.HTML)


@teach.callback_query(F.data.startswith('answer'))
async def answer_to_student(callback: CallbackQuery, state: FSMContext):
	if callback.data.startswith('answer'):
		await state.update_data(waiting_for_message=callback.data)
		await state.set_state(StudentAnswer.waiting_for_response)
		await callback.message.answer('Напишите ответ студенту')
		await callback.answer('')
	else:
		await callback.answer('Нажмите на кнопку "Ответить"')


@teach.message(StudentAnswer.waiting_for_response)
async def teacher_response(message: Message, state: FSMContext):
	await send_message_to_student(message)
	await message.answer('Ответ успешно отправлен')
	await state.clear()


@teach.message(F.text == 'Расписание')
async def cmd_desk(message: Message):
	if is_teacher(message.from_user.id):
		await message.answer('Выберите следующее действие:', reply_markup=kb.desk_question)
	else:
		await message.answer('У вас нет полномочий просматривать расписание!')


@teach.callback_query(F.data.startswith('desk_check'))
async def call_desk_check(callback: CallbackQuery):
	await callback.answer('')
	await callback.message.answer('В данный момент, расписание отсутствует')


@teach.callback_query(F.data.startswith('desk_upload'))
async def call_desk_upload(callback: CallbackQuery):
	await callback.answer('')
	await callback.message.answer('Отправьте файл в формате xlsx, чтобы загрузить расписание')


