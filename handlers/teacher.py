from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
import handlers.keyboards as kb
from config import ADMIN_ID
from config import bot
import json
from datetime import datetime
from .states import WorkTest, AdminCall, StudentContact
from handlers.create_data_base import (cur_tests, cur_users, cur_results,
                                       conn_tests, conn_users, cur_messages, conn_messages)

teach = Router()


@teach.message(F.text == 'Связь со студентами ☎️')
async def student_contact(message: Message, state: FSMContext):
    # Получаем список студентов из таблицы users
    cur_users.execute("SELECT user_id, user_full_name FROM users WHERE user_type = 'student'")
    students = cur_users.fetchall()

    # Формируем клавиатуру с инлайн-кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{full_name}", callback_data=f"send_to_student_{user_id}")]
        for user_id, full_name in students
    ])

    await message.answer("Выберите студента из списка:", reply_markup=keyboard)
    await state.set_state(StudentContact.waiting_for_student)


@teach.callback_query(lambda c: c.data.startswith("send_to_student_"))
async def send_to_student(callback_query: CallbackQuery, state: FSMContext):
    student_id = int(callback_query.data.split("_")[-1])
    await state.update_data(student_id=student_id)
    await state.set_state(StudentContact.waiting_for_message)
    await callback_query.message.answer("Напишите сообщение студенту")
    await callback_query.answer()


@teach.callback_query(F.data.startswith('answer'))
async def answer_to_student(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('answer'):
        await state.update_data(waiting_for_message=callback.data)
        await state.set_state(StudentContact.waiting_for_response)
        await callback.message.answer('Напишите сообщение студенту')
        await callback.answer('')
    else:
        await callback.answer('Нажмите на кнопку "Ответить"')


@teach.message(StudentContact.waiting_for_response)
async def send_message_to_student(message: Message, state: FSMContext):
    # Сохраняем сообщение преподавателя в таблицу messages
    data = await state.get_data()
    student_id = data.get('student_id')
    if student_id:
        cur_messages.execute("INSERT INTO messages (user_id, user_type, message) VALUES (?, ?, ?)",
                             (message.from_user.id, 'teacher', message.text))
        conn_messages.commit()

        # Отправляем сообщение студенту
        await send_message_to_student(message, student_id, 'преподаватель')
        await message.answer("Сообщение успешно отправлено.")
    else:
        await message.answer('Не удалось найти ID студента в базе данных')

    await state.clear()


async def send_message_to_student(message: Message, user_id: int, user_type: str):
    await bot.send_message(user_id, f'*Сообщение от {user_type},'
                                    f' {message.from_user.full_name}\n\n*'
                                    f' {message.text}',
                           reply_markup=kb.st_answer,
                           parse_mode=ParseMode.MARKDOWN)


@teach.callback_query(F.data == 'check_week_data')
async def data_check_week_data(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('<b>Расписание на понедельник:</b>\n'
                                  '1) Математика - Николай И.Н. 301 каб \n'
                                  '2) Русский язык - Иванова А.М. 105 каб.\n'
                                  '3) Информатика - Лебедев Н.О. 224 каб.\n'
                                  '4) Физкультура - Елисеев А.П. 111 каб.',
                                  parse_mode=ParseMode.HTML)


@teach.message(F.text == 'Рассылка группе 📢')
async def text_message_for_group_student(message: Message):
    await message.answer('<b>Выберите нужную группу для отправки рассылки</b>',
                         parse_mode=ParseMode.HTML, reply_markup=kb.groups_college)


@teach.message(F.text == 'Создать тест ➕')
async def text_create_test(message: Message, state: FSMContext):
    await state.set_state(WorkTest.name_quest)
    await message.answer(f'Напишите название теста\n'
                         f'*Примечание: Название теста не должно быть длиннее 63 символов!*',
                         reply_markup=kb.cancel,
                         parse_mode=ParseMode.MARKDOWN)


@teach.message(F.text == 'Выйти из создания теста 🙅')
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'*Создание теста прекращено*', parse_mode=ParseMode.MARKDOWN,
                         reply_markup=kb.teacher_panel())


@teach.message(WorkTest.name_quest)
async def test_name_quest(message: Message, state: FSMContext):
    name_quest = message.text.strip()
    if len(name_quest) > 63:
        await message.answer("Название теста не должно превышать 63 символа."
                             " Пожалуйста, введите название заново.")
    else:
        await state.update_data(name_quest=name_quest)
        await state.set_state(WorkTest.quest1)
        await message.answer('Отлично! теперь напишите вопрос №1')


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
    await state.set_state(WorkTest.quest2)
    await message.answer('Отлично, теперь напишите вопрос №2')


@teach.message(WorkTest.quest2)
async def test_quest2(message: Message, state: FSMContext):
    await state.update_data(question2=message.text)
    await state.set_state(WorkTest.q2_answer1)
    await message.answer('Напишите первый вариант ответа')


@teach.message(WorkTest.q2_answer1)
async def test_q2_answer1(message: Message, state: FSMContext):
    await state.update_data(q2_answer1=message.text)
    await state.set_state(WorkTest.q2_answer2)
    await message.answer('Напишите второй вариант ответа')


@teach.message(WorkTest.q2_answer2)
async def test_q2_answer2(message: Message, state: FSMContext):
    await state.update_data(q2_answer2=message.text)
    await state.set_state(WorkTest.q2_answer3)
    await message.answer('Напишите третий вариант ответа')


@teach.message(WorkTest.q2_answer3)
async def test_q2_answer3(message: Message, state: FSMContext):
    await state.update_data(q2_answer3=message.text)
    await state.set_state(WorkTest.q2_answer4)
    await message.answer('Напишите четвертый вариант ответа')


@teach.message(WorkTest.q2_answer4)
async def test_q2_answer4(message: Message, state: FSMContext):
    await state.update_data(q2_answer4=message.text)
    await state.set_state(WorkTest.quest3)
    await message.answer('Отлично, теперь напишите вопрос №3')


@teach.message(WorkTest.quest3)
async def test_quest3(message: Message, state: FSMContext):
    await state.update_data(question3=message.text)
    await state.set_state(WorkTest.q3_answer1)
    await message.answer('Теперь напишите первый вариант ответа')


@teach.message(WorkTest.q3_answer1)
async def test_q3_answer1(message: Message, state: FSMContext):
    await state.update_data(q3_answer1=message.text)
    await state.set_state(WorkTest.q3_answer2)
    await message.answer('Теперь напишите второй вариант ответа')


@teach.message(WorkTest.q3_answer2)
async def test_q3_answer2(message: Message, state: FSMContext):
    await state.update_data(q3_answer2=message.text)
    await state.set_state(WorkTest.q3_answer3)
    await message.answer('Теперь напишите третий вариант ответа')


@teach.message(WorkTest.q3_answer3)
async def test_q3_answer3(message: Message, state: FSMContext):
    await state.update_data(q3_answer3=message.text)
    await state.set_state(WorkTest.q3_answer4)
    await message.answer('Теперь напишите четвертый вариант ответа')


@teach.message(WorkTest.q3_answer4)
async def test_q3_answer4(message: Message, state: FSMContext):
    await state.update_data(q3_answer4=message.text)
    await state.set_state(WorkTest.quest4)
    await message.answer('Отлично, теперь напишите вопрос №4')


@teach.message(WorkTest.quest4)
async def test_quest4(message: Message, state: FSMContext):
    await state.update_data(question4=message.text)
    await state.set_state(WorkTest.q4_answer1)
    await message.answer('Напишите первый вариант ответа')


@teach.message(WorkTest.q4_answer1)
async def test_q4_answer1(message: Message, state: FSMContext):
    await state.update_data(q4_answer1=message.text)
    await state.set_state(WorkTest.q4_answer2)
    await message.answer('Напишите второй вариант ответа')


@teach.message(WorkTest.q4_answer2)
async def test_q4_answer2(message: Message, state: FSMContext):
    await state.update_data(q4_answer2=message.text)
    await state.set_state(WorkTest.q4_answer3)
    await message.answer('Напишите третий вариант ответа')


@teach.message(WorkTest.q4_answer3)
async def test_q4_answer3(message: Message, state: FSMContext):
    await state.update_data(q4_answer3=message.text)
    await state.set_state(WorkTest.q4_answer4)
    await message.answer('Напишите четвертый вариант ответа')


@teach.message(WorkTest.q4_answer4)
async def test_q4_answer4(message: Message, state: FSMContext):
    await state.update_data(q4_answer4=message.text)
    await state.set_state(WorkTest.quest5)
    await message.answer('Отлично, теперь напишите вопрос №5')


@teach.message(WorkTest.quest5)
async def test_quest5(message: Message, state: FSMContext):
    await state.update_data(question5=message.text)
    await state.set_state(WorkTest.q5_answer1)
    await message.answer('Напишите первый вариант ответа')


@teach.message(WorkTest.q5_answer1)
async def test_q5_answer1(message: Message, state: FSMContext):
    await state.update_data(q5_answer1=message.text)
    await state.set_state(WorkTest.q5_answer2)
    await message.answer('Напишите второй вариант ответа')


@teach.message(WorkTest.q5_answer2)
async def test_q5_answer2(message: Message, state: FSMContext):
    await state.update_data(q5_answer2=message.text)
    await state.set_state(WorkTest.q5_answer3)
    await message.answer('Напишите третий вариант ответа')


@teach.message(WorkTest.q5_answer3)
async def test_q5_answer3(message: Message, state: FSMContext):
    await state.update_data(q5_answer3=message.text)
    await state.set_state(WorkTest.q5_answer4)
    await message.answer('Напишите четвертый вариант ответа')


@teach.message(WorkTest.q5_answer4)
async def test_q5_answer4(message: Message, state: FSMContext):
    await state.update_data(q5_answer4=message.text)
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
            },
            {
                'question': data.get('question2'),
                'answers': [
                    data.get('q2_answer1', ''),
                    data.get('q2_answer2', ''),
                    data.get('q2_answer3', ''),
                    data.get('q2_answer4', '')
                ]
            },
            {
                'question': data.get('question3'),
                'answers': [
                    data.get('q3_answer1', ''),
                    data.get('q3_answer2', ''),
                    data.get('q3_answer3', ''),
                    data.get('q3_answer4', '')
                ]
            },
            {
                'question': data.get('question4'),
                'answers': [
                    data.get('q4_answer1', ''),
                    data.get('q4_answer2', ''),
                    data.get('q4_answer3', ''),
                    data.get('q4_answer4', '')
                ]
            },
            {
                'question': data.get('question5'),
                'answers': [
                    data.get('q5_answer1', ''),
                    data.get('q5_answer2', ''),
                    data.get('q5_answer3', ''),
                    data.get('q5_answer4', '')
                ]
            }
        ]
    }

    save_test(test_data)

    formatted_text = []
    for question_index, question in enumerate(test_data['questions'], start=1):
        formatted_text.append(f'*Вопрос {question_index}*: `{question["question"]}`')
        formatted_text.append(f'*Варианты ответа*:')
        for answer in question['answers']:
            formatted_text.append(f'- `{answer}`')
        formatted_text.append('')

    await message.answer(
        f'Составленный тест:\n\n{"\n".join(formatted_text)}',
        reply_markup=kb.teacher_panel(),
        parse_mode=ParseMode.MARKDOWN
    )


def save_test(test_data):
    cur_tests.execute("INSERT INTO tests (name, questions, created_at) VALUES (?, ?, ?)",
                      (test_data['name'],
                       json.dumps(test_data['questions']),
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn_tests.commit()


@teach.message(F.text == 'Список тестов 📖')
async def text_show_tests(message: Message):
    cur_tests.execute("SELECT id, name, created_at FROM tests")
    tests = cur_tests.fetchall()
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

    cur_tests.execute("SELECT name, questions FROM tests WHERE id = ?", (test_id,))
    name, questions_json = cur_tests.fetchone()
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
async def send_test_to_students(callback_query: CallbackQuery):
    test_id = int(callback_query.data.split("_")[-1])

    cur_tests.execute("SELECT name, questions FROM tests WHERE id = ?", (test_id,))
    test_name, questions_json = cur_tests.fetchone()

    cur_users.execute("SELECT user_id FROM users WHERE user_type = 'student'")
    student_ids = [row[0] for row in cur_users.fetchall()]

    for student_id in student_ids:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Начать тест', callback_data=f"start_test_{test_id}")]
        ])

        await bot.send_message(
            student_id,
            f"Вам пришел тест на прохождение '{test_name}'. Нажмите на кнопку, чтобы начать.",
            reply_markup=keyboard
        )

    await callback_query.message.edit_text("Тест отправлен студентам.")


@teach.callback_query(F.data == "back")
async def back_to_tests_list(callback_query: CallbackQuery):
    cur_tests.execute("SELECT id, name, created_at FROM tests")
    tests = cur_tests.fetchall()

    keyboard_tests = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{name} ({created_at})", callback_data=f"show_test_{test_id}")]
        for test_id, name, created_at in tests
    ])

    await callback_query.message.edit_text(
        "Выберите тест, чтобы просмотреть:",
        reply_markup=keyboard_tests
    )


@teach.message(F.text == 'Показать результаты ✅')
async def show_test_results(message: Message):
    cur_tests.execute("SELECT name FROM tests")
    test_names = [row[0] for row in cur_tests.fetchall()]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=test_name, callback_data=f"show_results_{test_name}")]
        for test_name in test_names
    ])

    await message.answer("Выберите тест, чтобы посмотреть результаты:", reply_markup=keyboard)


@teach.callback_query(lambda c: c.data.startswith("show_results_"))
async def show_selected_test_results(callback_query: CallbackQuery):
    test_name = callback_query.data.split("_")[-1]

    cur_results.execute("""
        SELECT full_name, answer_text, created_at 
        FROM results
        WHERE test_name = ?
    """, (test_name,))
    results = cur_results.fetchall()

    if results:
        formatted_results = f"Тест: {test_name}\n\n"
        current_student = None
        for row in results:
            student_name = row[0]
            if student_name != current_student:
                if current_student is not None:
                    formatted_results += "\n"
                formatted_results += f"Студент: {student_name}\n"
                current_student = student_name
            if row[1]:
                formatted_results += f"➖ *{row[1]}*\n"
            else:
                formatted_results += f"➖ *Ответ отсутствует*\n"
            formatted_results += f"  _Дата: {row[2]}_ ⏳\n"
    else:
        formatted_results = f"Для теста '{test_name}' нет результатов."

    await callback_query.message.answer(formatted_results.strip(), parse_mode=ParseMode.MARKDOWN)
    await callback_query.answer('')


@teach.message(F.text == "Связь с админом ☎️")
async def text_call_admin(message: Message, state: FSMContext):
    await state.set_state(AdminCall.wait_to_message)
    await state.update_data(user_name=message.from_user.full_name)
    await message.answer('Напишите сообщение администратору')


@teach.message(AdminCall.wait_to_message)
async def send_message_to_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    user_name = data.get('user_name')
    admin_chat_id = ADMIN_ID
    await bot.send_message(chat_id=admin_chat_id, text=f"*Новое сообщение от {user_name}:*\n\n{message.text}",
                           parse_mode=ParseMode.MARKDOWN)
    await message.answer("Ваше сообщение отправлено администратору. Ожидайте ответа.")
    await state.clear()
