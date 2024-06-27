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
              answer_text TEXT,
              created_at TEXT)''')
conn.commit()


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

    conn_results = sqlite3.connect('data/data_base/results.db')
    c_results = conn_results.cursor()

    c_results.execute("SELECT COUNT(*) FROM results WHERE test_id = ? AND full_name = ?",
                      (test_id, callback_query.from_user.full_name))
    count = c_results.fetchone()[0]

    if count > 0:
        c_results.execute("""
            SELECT answer_text, created_at 
            FROM results
            WHERE test_id = ? AND full_name = ?
            ORDER BY id
        """, (test_id, callback_query.from_user.full_name))
        results = c_results.fetchall()

        formatted_result = f"Вы уже проходили этот тест:\n\n"
        for answer_text, created_at in results:
            formatted_result += f"- {answer_text}\n"
            formatted_result += f"  **Дата:** {created_at}\n\n"
        await callback_query.message.answer(formatted_result.strip(), parse_mode=ParseMode.MARKDOWN)
    else:
        conn_tests = sqlite3.connect('data/data_base/tests.db')
        c_tests = conn_tests.cursor()

        c_tests.execute("SELECT name, questions FROM tests WHERE id = ?", (test_id,))
        test_name, questions_json = c_tests.fetchone()
        questions = json.loads(questions_json)

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
            [InlineKeyboardButton(text=answer, callback_data=f"answer_{test_id}_{current_question}_{i}")]
            for i, answer in enumerate(question['answers'])
        ])

        msg = await message.answer(
            f"*Тест: {test_name}*\n\n*Вопрос {current_question+1}:* *{question['question']}*\n\nВарианты ответа:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        await state.update_data(question_message_id=msg.message_id)
    else:
        question_message_id = (await state.get_data()).get('question_message_id')
        if question_message_id:
            await bot.delete_message(chat_id=message.chat.id, message_id=question_message_id)

        await state.clear()
        await message.answer("*Вы успешно закончили прохождение теста!*\n"
                             "Ваши результаты были направлены преподавателю.",
                             parse_mode=ParseMode.MARKDOWN)


@std.callback_query(lambda c: c.data.startswith("answer_"))
async def process_student_answer(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    test_id = data['test_id']
    test_name = data['test_name']
    questions = data['questions']
    current_question = data['current_question']
    selected_answer_index = int(callback_query.data.split("_")[-1])
    selected_answer_text = questions[current_question]['answers'][selected_answer_index]

    conn_results = sqlite3.connect('data/data_base/results.db')
    c_results = conn_results.cursor()

    c_results.execute("INSERT INTO results (test_id, test_name, full_name, answer, answer_text, created_at)"
                      " VALUES (?, ?, ?, ?, ?, ?)",
                      (test_id, test_name, callback_query.from_user.full_name, selected_answer_index+1, selected_answer_text,
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn_results.commit()

    if current_question < len(questions) - 1:
        await state.update_data(current_question=current_question+1)
        question = questions[current_question+1]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=answer, callback_data=f"answer_{test_id}_{current_question+1}_{i}")]
            for i, answer in enumerate(question['answers'])
        ])

        await callback_query.message.edit_text(
            f"*Тест: {test_name}*\n\n*Вопрос {current_question+2}:* *{question['question']}*\n\nВарианты ответа:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await state.clear()
        await callback_query.message.edit_text("*Вы успешно закончили прохождение теста!*\n"
                                               "Ваши результаты были направлены преподавателю.",
                                               parse_mode=ParseMode.MARKDOWN)


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
