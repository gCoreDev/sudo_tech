from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
import os
from aiogram import F, Router
from aiogram.filters import CommandStart, Command, CommandObject, StateFilter
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
import app.keyboards as kb

load_dotenv()

std = Router()

STUDENT_ID = int(os.getenv('STUDENT_ID'))
bot = Bot(token=os.getenv('TOKEN'))
ADMIN_ID = int(os.getenv('ADMIN_ID'))


@std.message(F.text == 'Показать тесты')
async def show_test(message: Message):
	await message.answer('На данный момент тестов для прохождения нет')


async def send_message_to_teacher(message: Message):
	await bot.send_message(ADMIN_ID, f'<b>Сообщение от студента,'
									f' {message.from_user.full_name}\n</b>'
									f' {message.text}',
						   			reply_markup=kb.answer,
						   			parse_mode=ParseMode.HTML)


@std.message(F.text == 'Связь с преподавателем')
async def teacher_contact(message: Message):
	await message.answer('Напишите сообщение преподавателю')


@std.message()
async def teacher_connect_text(message: Message):
	if message.text.startswith('Связь с преподавателем'):
		return
	await send_message_to_teacher(message)
	await message.answer('Сообщение успешно отправлено')


