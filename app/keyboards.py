from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
						   InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton(text='Личный кабинет')],
	[KeyboardButton(text='Узнать о боте'),
	 KeyboardButton(text='Сайт колледжа')],
	[KeyboardButton(text='Новости колледжа')]
],
	resize_keyboard=True,
	input_field_placeholder='Выберите пункт меню')

site = InlineKeyboardMarkup(inline_keyboard=[
	[InlineKeyboardButton(text='Перейти на сайт колледжа', url='https://www.ekvl.ru/')]
])

group = InlineKeyboardMarkup(inline_keyboard=[
	[InlineKeyboardButton(text='Перейти в канал колледжа:', url='https://t.me/EnergyCollege')]
])

data = ('Показать пользователей', 'Добавить пользователя',
		'Удалить пользователя', 'Сделать рассылку', 'Назад')

answer = InlineKeyboardMarkup(inline_keyboard=[
	[InlineKeyboardButton(text='Ответить', callback_data='answer')]
])

st_answer = InlineKeyboardMarkup(inline_keyboard=[
	[InlineKeyboardButton(text='Ответить', callback_data='st_answer')]
])


def admin_panel():
	keyboard = ReplyKeyboardBuilder()
	for admin_panel in data:
		keyboard.add(KeyboardButton(text=admin_panel))
	return keyboard.adjust(2).as_markup(resize_keyboard=True)


data_std = ('Показать тесты', 'Связь с преподавателем',
			'Учебные материалы', 'Расписание пар',
			'Меню столовой', 'Назад')


def std_panel():
	keyboard = ReplyKeyboardBuilder()
	for std_panel in data_std:
		keyboard.add(KeyboardButton(text=std_panel))
	return keyboard.adjust(2).as_markup(resize_keyboard=True)


key_teacher = ('Создать тест', 'Расписание', 'Рассылка группе', 'Связь с админом')


def teacher_panel():
	keyboard = ReplyKeyboardBuilder()
	for teacher_panel in key_teacher:
		keyboard.add(KeyboardButton(text=teacher_panel))
	return keyboard.adjust(2).as_markup(resize_keyboard=True)


docs_panel = InlineKeyboardMarkup(inline_keyboard=[
	[InlineKeyboardButton(text='Реферат', callback_data='Ref')],
	[InlineKeyboardButton(text='Курсовая', callback_data='Kur')],
	[InlineKeyboardButton(text='Отчет по практике', callback_data='Otc')],
	[InlineKeyboardButton(text='Дипломная работа', callback_data='Dip')],
	[InlineKeyboardButton(text='Оформление документа', callback_data='Gos')]
])
