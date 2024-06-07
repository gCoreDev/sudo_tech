from aiogram import Bot, types
from aiogram.enums.parse_mode import ParseMode
import os
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
import app.keyboards as kb

load_dotenv()

std = Router()

STUDENT_ID = int(os.getenv('STUDENT_ID'))
bot = Bot(token=os.getenv('TOKEN'))
ADMIN_ID = int(os.getenv('ADMIN_ID'))
TEACHER_ID = int(os.getenv('TEACHER_ID'))


@std.message(F.text == 'Показать тесты')
async def show_test(message: Message):
	await message.answer('На данный момент тестов для прохождения нет')


class TeacherContact(StatesGroup):
	waiting_for_message = State()
	waiting_for_response1 = State()


async def send_message_to_teacher(message: Message):
	await bot.send_message(TEACHER_ID, f'<b>Сообщение от студента,'
									f' {message.from_user.full_name}\n</b>'
									f' {message.text}',
						   			reply_markup=kb.answer,
						   			parse_mode=ParseMode.HTML)


@std.callback_query(F.data.startswith('st_answer'))
async def answer_to_teacher(callback: CallbackQuery, state: FSMContext):
	if callback.data.startswith('st_answer'):
		await state.update_data(waiting_for_response1=callback.data)
		await state.set_state(TeacherContact.waiting_for_response1)
		await callback.message.answer('Напишите ответ преподавателю')
		await callback.answer('')
	else:
		await callback.answer('Нажмите на кнопку "Ответить"')


@std.message(TeacherContact.waiting_for_response1)
async def student_response(message: Message, state: FSMContext):
	await send_message_to_teacher(message)
	await message.answer('Ответ успешно отправлен')
	await state.clear()


@std.message(F.text == 'Связь с преподавателем')
async def teacher_contact(message: Message, state: FSMContext):
	await state.update_data(waiting_for_message=message.text)
	await state.set_state(TeacherContact.waiting_for_message)
	await message.answer('Напишите сообщение преподавателю')


@std.message(TeacherContact.waiting_for_message)
async def teacher_connect_text(message: Message, state: FSMContext):
	if message.text.startswith('Связь с преподавателем'):
		return
	await send_message_to_teacher(message)
	await message.answer('Сообщение успешно отправлено')
	await state.clear()


@std.message(F.text == 'Учебные материалы')
async def cmd_docs(message: Message):
	await message.answer('Учебные документы и шаблоны', reply_markup=kb.docs_panel)






