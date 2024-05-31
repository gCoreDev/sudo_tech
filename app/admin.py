import os
from aiogram import F, Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import app.keyboards as kb
from app.student import bot

load_dotenv()

admin = Router()

ADMIN_ID = int(os.getenv('ADMIN_ID'))
STUDENT_ID = int(os.getenv('STUDENT_ID'))


@admin.message(Command('admin'))
async def cmd_admin(message: Message):
	if ADMIN_ID == message.from_user.id:
		await message.answer('Вы в админ панеле!')
	else:
		await message.answer('В доступе отказано!')


@admin.message(F.text == 'Личный кабинет')
async def per_acc_adm(message: Message):
	if ADMIN_ID == message.from_user.id:
		await message.answer('Вы в админ панели',
							 reply_markup=kb.admin_panel())
	elif STUDENT_ID == message.from_user.id:
		await message.answer(f'Добро пожаловать, {message.from_user.full_name}, студент!',
							 reply_markup=kb.std_panel())
	else:
		await message.answer('У вас недостаточно прав')


class StudentAnswer(StatesGroup):
	waiting_for_response = State()


async def send_message_to_student(message: Message):
	await bot.send_message(STUDENT_ID, f'<b>Сообщение от преподавателя,'
									f' {message.from_user.full_name}\n</b>'
									f' {message.text}',
									parse_mode=ParseMode.HTML)


@admin.callback_query(F.data.startswith('answer'))
async def answer_to_student(callback: CallbackQuery, state: FSMContext):
	if callback.data.startswith('answer'):
		await state.update_data(waiting_for_message=callback.data)
		await state.set_state(StudentAnswer.waiting_for_response)
		await callback.message.answer('Напишите ответ студенту')
		await callback.answer('')
	else:
		await callback.answer('Нажмите на кнопку "Ответить"')


@admin.message(StudentAnswer.waiting_for_response)
async def teacher_response(message: Message, state: FSMContext):
	await send_message_to_student(message)
	await message.answer('Ответ успешно отправлен')
	await state.clear()




