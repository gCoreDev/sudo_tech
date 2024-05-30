import os
from aiogram import F, Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
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


@admin.callback_query(F.data == 'answer')
async def answer_to_student(callback: CallbackQuery):
	await callback.answer('В разработке')

