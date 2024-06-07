import os
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv
import data.keyboards as kb

load_dotenv()

admin = Router()

ADMIN_ID = int(os.getenv('ADMIN_ID'))
STUDENT_ID = int(os.getenv('STUDENT_ID'))
TEACHER_ID = int(os.getenv('TEACHER_ID'))


@admin.message(Command('admin'))
async def cmd_admin(message: Message):
	if ADMIN_ID == message.from_user.id:
		await message.answer('Вы в админ панели!')
	else:
		await message.answer('В доступе отказано!')


@admin.message(F.text == 'Личный кабинет')
async def per_acc_adm(message: Message):
	if ADMIN_ID == message.from_user.id:
		await message.answer('Вы в админ панели',
							 reply_markup=kb.admin_panel())
	elif STUDENT_ID == message.from_user.id:
		await message.answer(f'Добро пожаловать,'
							 f' {message.from_user.full_name}, студент!',
							 reply_markup=kb.std_panel())
	elif TEACHER_ID == message.from_user.id:
		await message.answer(f'Добро пожаловать преподаватель,'
							 f' <b>{message.from_user.full_name}!</b>',
							 parse_mode=ParseMode('HTML'),
							 reply_markup=kb.teacher_panel())
	else:
		await message.answer('Вы отсутствуете в списках ЭнергоБота')





