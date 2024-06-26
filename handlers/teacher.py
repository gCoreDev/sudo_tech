from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
import handlers.keyboards as kb
from config import TOKEN, STUDENT_ID
import json
import sqlite3
from datetime import datetime

bot = Bot(token=TOKEN)

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


@teach.message(F.text == 'Расписание')
async def week_plan(message: Message):
    await message.answer('Выберите действие над расписанием', reply_markup=kb.week_plan)


@teach.callback_query(F.data == 'upload_week_plan')
async def data_upload_week_plan(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Чтобы загрузить расписание, отправьте мне файл в формате .xlxs')


@teach.callback_query(F.data == 'check_week_data')
async def data_check_week_data(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('<b>Расписание на понедельник:</b>\n'
                                  '1) Математика - Николай И.Н. 301 каб \n'
                                  '2) Русский язык - Иванова А.М. 105 каб.\n'
                                  '3) Информатика - Лебедев Н.О. 224 каб.\n'
                                  '4) Физукультура - Елисеев А.П. 111 каб.',
                                  parse_mode=ParseMode.HTML)


@teach.message(F.text == 'Рассылка группе')
async def text_message_for_group_student(message: Message):
    await message.answer('<b>Выберите нужную группу для отправки рассылки</b>',
                         parse_mode=ParseMode.HTML, reply_markup=kb.groups_college)


conn = sqlite3.connect('data/data_base/tests.db')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS tests 
    (id INTEGER PRIMARY KEY,
    name TEXT,
    questions TEXT,
    created_at TEXT)
''')


conn.commit()


class WorkTest(StatesGroup):
    name_quest = State()
    quest1 = State()
    q1_answer1 = State()
    q1_answer2 = State()
    q1_answer3 = State()
    q1_answer4 = State()
    quest2 = State()
    q2_answer1 = State()
    q2_answer2 = State()
    q2_answer3 = State()
    q2_answer4 = State()
    quest3 = State()
    q3_answer1 = State()
    q3_answer2 = State()
    q3_answer3 = State()
    q3_answer4 = State()


@teach.message(F.text == 'Создать тест')
async def text_create_test(message: Message, state: FSMContext):
    await state.set_state(WorkTest.name_quest)
    await message.answer('Напишите название теста', reply_markup=kb.cancel)


@teach.message(F.text == 'Выйти из создания теста')
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'<b>Создание теста прекращено</b>', parse_mode=ParseMode.HTML,
                         reply_markup=kb.teacher_panel())


@teach.message(WorkTest.name_quest)
async def test_name_quest(message: Message, state: FSMContext):
    await state.update_data(name_quest=message.text)
    await state.set_state(WorkTest.quest1)
    await message.answer('Отлично! Напишите первый вопрос')


@teach.message(WorkTest.quest1)
async def test_quest1(message: Message, state: FSMContext):
    await state.update_data(question1=message.text)
    await state.set_state(WorkTest.q1_answer1)
    await message.answer('Напишите первый вариант ответа')


@teach.message(WorkTest.q1_answer1)
async def test_q1_answer1(message: Message, state: FSMContext):
    await state.update_data(q1_answer1=message.text)
    await state.set_state(WorkTest.q1_answer2)
    await message.answer('Далее напишите второй вариант ответа')


@teach.message(WorkTest.q1_answer2)
async def test_q1_answer2(message: Message, state: FSMContext):
    await state.update_data(q1_answer2=message.text)
    await state.set_state(WorkTest.q1_answer3)
    await message.answer('Теперь напишите третий вариант ответа')


@teach.message(WorkTest.q1_answer3)
async def test_q1_answer3(message: Message, state: FSMContext):
    await state.update_data(q1_answer3=message.text)
    await state.set_state(WorkTest.q1_answer4)
    await message.answer('Напишите четвертый вариант ответа')


@teach.message(WorkTest.q1_answer4)
async def test_q1_answer4(message: Message, state: FSMContext):
    await state.update_data(q1_answer4=message.text)
    data = await state.get_data()
    await state.clear()

    test_data = {
        'name': data['name_quest'],
        'questions': [
            {
                'question': data['question1'],
                'answers': [
                    data['q1_answer1'],
                    data['q1_answer2'],
                    data['q1_answer3'],
                    data['q1_answer4']
                ]
            }
        ]
    }

    save_test(test_data)

    formated_text = []
    for key, value in test_data['questions'][0].items():
        if key == 'answers':
            formated_text.append(f'*Варианты ответа*:')
            for answer in value:
                formated_text.append(f'- `{answer}`')
        else:
            formated_text.append(f'*{key}*: `{value}`')
    await message.answer(
        f'Составленный тест:\n\n{"\n".join(formated_text)}',
        reply_markup=kb.teacher_panel(),
        parse_mode=ParseMode.MARKDOWN
    )


def save_test(test_data):
    cur.execute("INSERT INTO tests (name, questions, created_at) VALUES (?, ?, ?)",
                (test_data['name'],
                 json.dumps(test_data['questions']),
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()


@teach.message(F.text == 'Список тестов')
async def text_show_tests(message: Message):
    cur.execute("SELECT id, name, created_at FROM tests")
    tests = cur.fetchall()
    if not tests:
        await message.answer('Ни одного теста не было найдено')
        return
    keyboard_tests = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{name} ({created_at})", callback_data=f"show_test_{test_id}")]
        for test_id, name, created_at in tests
    ])
    await message.answer("Выберите тест, чтобы просмотреть:", reply_markup=keyboard_tests)


@teach.callback_query(F.data.startswith("show_test_"))
async def show_selected_test(callback_query: CallbackQuery):
    test_id = int(callback_query.data.split("_")[-1])

    cur.execute("SELECT name, questions FROM tests WHERE id = ?", (test_id,))
    name, questions_json = cur.fetchone()
    questions = json.loads(questions_json)

    formatted_test = []
    for question in questions:
        formatted_test.append(f"*Вопрос*: {question['question']}")
        formatted_test.append("*Варианты ответа*:")
        for answer in question['answers']:
            formatted_test.append(f"- `{answer}`")
        formatted_test.append("")

    await callback_query.message.edit_text(
        f"Тест: *{name}*\n\n{'\n'.join(formatted_test)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить тест студентам", callback_data=f"send_test_{test_id}")],
            [InlineKeyboardButton(text="Назад", callback_data="back")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )


@teach.callback_query(F.data.startswith("send_test_"))
async def send_test_to_students(message: Message, state: FSMContext):
    conn_tests = sqlite3.connect('data/data_base/tests.db')
    c_tests = conn_tests.cursor()

    c_tests.execute("SELECT id, name, questions FROM tests")
    tests = c_tests.fetchall()

    for test_id, test_name, questions_json in tests:
        questions = json.loads(questions_json)

        conn_users = sqlite3.connect('data/data_base/users.db')
        c_users = conn_users.cursor()

        c_users.execute("SELECT user_id FROM users WHERE user_type = 'student'")
        student_ids = [row[0] for row in c_users.fetchall()]

        for student_id in student_ids:
            await bot.send_message(
                student_id,
                f"*Уведомление*\n*Вам направили тест: {test_name}*\n\nПожалуйста, сделайте его в ближайшее время,\n"
                f"Протйи тест вы можете нажав по кнопке показать тесты.",
                parse_mode=ParseMode.MARKDOWN
            )
        conn_users.close()

    conn_tests.close()
    await message.answer("Тесты отправлены студентам.")


@teach.callback_query(F.data == "back")
async def back_to_tests_list(callback_query: CallbackQuery):
    cur.execute("SELECT id, name, created_at FROM tests")
    tests = cur.fetchall()

    keyboard_tests = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{name} ({created_at})", callback_data=f"show_test_{test_id}")]
        for test_id, name, created_at in tests
    ])

    await callback_query.message.edit_text(
        "Выберите тест, чтобы просмотреть:",
        reply_markup=keyboard_tests
    )


@teach.message(F.text == 'Показать результаты')
async def show_test_results(message: Message):
    conn_tests = sqlite3.connect('data/data_base/tests.db')
    c_tests = conn_tests.cursor()

    c_tests.execute("SELECT name FROM tests")
    test_names = [row[0] for row in c_tests.fetchall()]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=test_name, callback_data=f"show_results_{test_name}")]
        for test_name in test_names
    ])

    await message.answer("Выберите тест, чтобы посмотреть результаты:", reply_markup=keyboard)


@teach.callback_query(lambda c: c.data.startswith("show_results_"))
async def show_selected_test_results(callback_query: CallbackQuery, state: FSMContext):
    test_name = callback_query.data.split("_")[-1]

    conn_results = sqlite3.connect('data/data_base/results.db')
    c_results = conn_results.cursor()

    c_results.execute("SELECT full_name, answer, created_at FROM results WHERE test_name = ?",
                      (test_name,))
    results = c_results.fetchall()

    if results:
        formatted_results = f"Тест: {test_name}\n\n"
        for row in results:
            formatted_results += f"Студент: {row[0]}\n"
            formatted_results += f"Ответ: {row[1]}\n"
            formatted_results += f"Дата: {row[2]}\n\n"
    else:
        formatted_results = f"Для теста '{test_name}' нет результатов."

    await callback_query.message.answer(formatted_results.strip())
    await callback_query.answer('')
