from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
import os
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
import data.keyboards as kb

load_dotenv()

STUDENT_ID = int(os.getenv('STUDENT_ID'))
bot = Bot(token=os.getenv('TOKEN'))
ADMIN_ID = int(os.getenv('ADMIN_ID'))
TEACHER_ID = int(os.getenv('TEACHER_ID'))

teach = Router()


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
