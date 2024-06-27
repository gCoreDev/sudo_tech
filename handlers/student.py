import json
from datetime import datetime
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import handlers.keyboards as kb
from config import TOKEN, TEACHER_ID
import sqlite3

std = Router()

bot = Bot(token=TOKEN)

conn_results = sqlite3.connect('data/data_base/results.db')
cur_results = conn_results.cursor()

conn = sqlite3.connect('data/data_base/results.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS results
             (id INTEGER PRIMARY KEY,
              test_id INTEGER,
              test_name TEXT,
              full_name TEXT,
              answer TEXT,
              created_at TEXT)''')

conn.commit()


class TeacherContact(StatesGroup):
    waiting_for_message = State()
    waiting_for_response1 = State()


@std.message(F.text == 'Показать тесты')
async def show_test(message: Message):
    await message.answer("*Выберите тест, который хотите пройти.*", parse_mode=ParseMode.MARKDOWN)

    conn_tests = sqlite3.connect('data/data_base/tests.db')
    c_tests = conn_tests.cursor()

    c_tests.execute("SELECT id, name FROM tests")
    tests = c_tests.fetchall()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=test_name, callback_data=f"start_test_{test_id}")]
        for test_id, test_name in tests
    ])

    await message.answer("Доступные тесты:", reply_markup=keyboard)


@std.callback_query(lambda c: c.data.startswith("start_test_"))
async def start_test(callback_query: CallbackQuery, state: FSMContext):
    test_id = int(callback_query.data.split("_")[-1])

    conn_tests = sqlite3.connect('data/data_base/tests.db')
    c_tests = conn_tests.cursor()

    c_tests.execute("SELECT name, questions FROM tests WHERE id = ?", (test_id,))
    test_name, questions_json = c_tests.fetchone()
    questions = json.loads(questions_json)

    conn_results = sqlite3.connect('data/data_base/results.db')
    c_results = conn_results.cursor()

    c_results.execute("SELECT * FROM results WHERE test_id = ? AND full_name = ?", (test_id, callback_query.from_user.full_name))
    if c_results.fetchone():
        await callback_query.answer("Вы уже проходили этот тест.")
        conn_tests.close()
        conn_results.close()
        return

    await state.update_data(test_id=test_id, test_name=test_name, questions=questions, current_question=0)

    await show_question(callback_query.message, state)

    conn_tests.close()
    conn_results.close()
    await callback_query.answer('')


async def show_question(message: Message, state: FSMContext):
    data = await state.get_data()
    test_id = data['test_id']
    test_name = data['test_name']
    questions = data['questions']
    current_question = data['current_question']

    if current_question < len(questions):
        question = questions[current_question]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=answer, callback_data=f"answer_{answer}")]
            for answer in question['answers']
        ])

        await state.clear()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить тест", callback_data="delete_test")]
        ])
        await message.answer("*Вы успешно закончили прохождение теста!*\n"
                             "Ваши результаты были направлены преподавателю.\n\n"
                             "Нажмите кнопку, чтобы скрыть тест из списка доступных.",
                             reply_markup=keyboard,
                             parse_mode=ParseMode.MARKDOWN)


@std.callback_query(lambda c: c.data == "delete_test")
async def delete_test(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    test_id = data['test_id']

    await callback_query.message.delete()
    await callback_query.answer("Тест успешно скрыт.")

    await state.update_data(hidden_tests=test_id)


@std.callback_query(lambda c: c.data.startswith("answer_"))
async def process_student_answer(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    test_id = data.get('test_id', None)
    test_name = data['test_name']
    questions = data['questions']
    current_question = data['current_question']

    if test_id is None:
        await callback_query.answer("Тест не найден.")
        return

    selected_answer = callback_query.data.split("_")[-1]

    conn_results = sqlite3.connect('data/data_base/results.db')
    c_results = conn_results.cursor()

    c_results.execute("SELECT * FROM results WHERE test_id = ? AND full_name = ?", (test_id, callback_query.from_user.full_name))
    if c_results.fetchone():
        await callback_query.answer("Вы уже проходили этот тест.")
        conn_results.close()
        return

    c_results.execute("INSERT INTO results (test_id, test_name, full_name, answer, created_at)"
                      " VALUES (?, ?, ?, ?, ?)",
                      (test_id, test_name, callback_query.from_user.full_name, selected_answer,
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn_results.commit()

    await state.update_data(current_question=current_question+1)
    await show_question(callback_query.message, state)
    await callback_query.answer('')
    conn_results.close()


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


@std.message(F.text == 'Расписание пар')
async def text_week_plan(message: Message):
    await message.answer('<b>Расписание на понедельник:</b>\n'
                         '1) Математика - Николай И.Н. 301 каб \n'
                         '2) Русский язык - Иванова А.М. 105 каб.\n'
                         '3) Информатика - Лебедев Н.О. 224 каб.\n'
                         '4) Физкультура - Елисеев А.П. 111 каб.',
                         parse_mode=ParseMode.HTML)


@std.message(F.text == 'Меню столовой')
async def text_menu(message: Message):
    await message.answer('<b>Меню на сегодня:\n</b>'
                         '1)Борщ со сметаной 🍜\n'
                         '2)Макароны с куриной котлетой 🍝\n'
                         '3)Компот 🧃',
                         parse_mode=ParseMode.HTML)
