from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Личный кабинет 👤')],
    [KeyboardButton(text='Узнать о боте 📖'),
     KeyboardButton(text='Сайт колледжа 💻')],
    [KeyboardButton(text='Новости колледжа 📢')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню')

site = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Перейти на сайт колледжа 💻', url='https://www.ekvl.ru/')]
])

group = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Перейти в канал колледжа 👨‍💻', url='https://t.me/EnergyCollege')]
])

data = ('Показать пользователей 👤',
        'Изменить тип пользователя ✏️',
        'Удалить пользователя ✖️',
        'Сделать рассылку 📢',
        'Погода 🌤',
        'Расписание 🗓',
        'Назад 🔙')

st_answer = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ответить 📞", callback_data='st_answer')]
])


def admin_panel():
    keyboard = ReplyKeyboardBuilder()
    for admin_panel in data:
        keyboard.add(KeyboardButton(text=admin_panel))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


data_std = ('Показать тесты 🧑‍💻',
            # 'Связь с преподавателем ☎️',
            'Погода 🌤',
            'Учебные материалы 📚',
            'Расписание пар 🗓',
            'Меню столовой 🍫',
            'Назад 🔙')


def std_panel():
    keyboard = ReplyKeyboardBuilder()
    for std_panel in data_std:
        keyboard.add(KeyboardButton(text=std_panel))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


key_teacher = ['Создать тест ➕',
               'Список тестов 📖',
               'Показать результаты ✅',
               # 'Связь со студентами ☎️',
               'Рассылка группе 📢',
               'Погода 🌤',
               'Связь с админом ☎️',
               'Назад 🔙']


def teacher_panel():
    keyboard = ReplyKeyboardBuilder()
    for teacher_panel in key_teacher:
        keyboard.add(KeyboardButton(text=teacher_panel))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


docs_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Реферат 📗', callback_data='Ref')],
    [InlineKeyboardButton(text='Курсовая 📓', callback_data='Kur')],
    [InlineKeyboardButton(text='Отчет по практике 📕', callback_data='Otc')],
    [InlineKeyboardButton(text='Дипломная работа 📙', callback_data='Dip')],
    [InlineKeyboardButton(text='Оформление документа 📘', callback_data='Gos')]
])

week_plan = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Загрузить 🆕', callback_data='upload_week_plan'),
        InlineKeyboardButton(text='Посмотреть 👀', callback_data='check_week_plan')
    ],
    [
        InlineKeyboardButton(text='Удалить 🗑', callback_data='del_week_plan')
    ]
])

groups_college = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='231-КС-21', callback_data='231-ks-21')
    ],
    [
        InlineKeyboardButton(text='142-СК-19', callback_data='142-sk-19')
    ],
    [
        InlineKeyboardButton(text='111-МВ-24', callback_data='111-mv-24')
    ]
])

cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Выйти из создания теста 🙅')]
], resize_keyboard=True)
