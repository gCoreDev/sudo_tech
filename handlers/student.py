import json
from datetime import datetime
from config import bot
from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import handlers.keyboards as kb
from .states import TeacherContact
from handlers.create_data_base import (cur_tests, cur_messages, cur_results, cur_users,
                                       conn_tests, conn_messages, conn_results, conn_users)

std = Router()


@std.message(F.text == 'Показать тесты 🧑‍💻')
async def show_test(message: Message):
    await message.answer("*Выберите тест, который хотите пройти.*", parse_mode=ParseMode.MARKDOWN)

    cur_tests.execute("SELECT id, name FROM tests")
    tests = cur_tests.fetchall()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=test_name, callback_data=f"start_test_{test_id}")]
        for test_id, test_name in tests
    ])
    await message.answer("Доступные тесты:", reply_markup=keyboard)


@std.callback_query(lambda c: c.data.startswith("start_test_"))
async def start_test(callback_query: CallbackQuery, state: FSMContext):
    test_id = int(callback_query.data.split("_")[-1])

    cur_results.execute("SELECT COUNT(*) FROM results WHERE test_id = ? AND full_name = ?",
                        (test_id, callback_query.from_user.full_name))
    count = cur_results.fetchone()[0]

    if count > 0:
        cur_results.execute("""
            SELECT answer_text, created_at 
            FROM results
            WHERE test_id = ? AND full_name = ?
            ORDER BY id
        """, (test_id, callback_query.from_user.full_name))
        results = cur_results.fetchall()

        formatted_result = f"Вы уже проходили этот тест:\n\n"
        for answer_text, created_at in results:
            formatted_result += f"➖ *{answer_text}*\n"
            formatted_result += f"  _Дата: {created_at}_ ⏳\n\n"
        await callback_query.message.answer(formatted_result.strip(), parse_mode=ParseMode.MARKDOWN)
    else:
        cur_tests.execute("SELECT name, questions FROM tests WHERE id = ?", (test_id,))
        test_name, questions_json = cur_tests.fetchone()
        questions = json.loads(questions_json)

        await state.update_data(test_id=test_id, test_name=test_name, questions=questions, current_question=0)

        await show_question(callback_query.message, state)

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
            f"*Тест: {test_name}*\n\n*Вопрос {current_question + 1}:* *{question['question']}*\n\nВарианты ответа:",
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
    if 'test_id' in data:
        test_id = data['test_id']
        test_name = data['test_name']
        questions = data['questions']
        current_question = data['current_question']
        selected_answer_index = int(callback_query.data.split("_")[-1])
        selected_answer_text = questions[current_question]['answers'][selected_answer_index]

        cur_results.execute("INSERT INTO results (test_id, test_name, full_name, answer, answer_text, created_at)"
                            " VALUES (?, ?, ?, ?, ?, ?)",
                            (test_id, test_name, callback_query.from_user.full_name, selected_answer_index + 1,
                             selected_answer_text,
                             datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn_results.commit()

        if current_question < len(questions) - 1:
            await state.update_data(current_question=current_question + 1)
            question = questions[current_question + 1]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=answer, callback_data=f"answer_{test_id}_{current_question + 1}_{i}")]
                for i, answer in enumerate(question['answers'])
            ])

            await callback_query.message.edit_text(
                f"*Тест: {test_name}*\n\n*Вопрос {current_question + 2}:* *{question['question']}*\n\nВарианты ответа:",
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await state.clear()
            await callback_query.message.edit_text("*Вы успешно закончили прохождение теста!*\n"
                                                   "Ваши результаты были направлены преподавателю.",
                                                   parse_mode=ParseMode.MARKDOWN)
    else:
        await callback_query.answer("Ошибка: Тест не найден.")


@std.message(F.text == 'Связь с преподавателем ☎️')
async def teacher_contact(message: Message, state: FSMContext):
    # Получаем список преподавателей из таблицы users
    cur_users.execute("SELECT user_id, user_full_name FROM users WHERE user_type = 'teacher'")
    teachers = cur_users.fetchall()

    # Формируем клавиатуру с инлайн-кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{full_name}", callback_data=f"send_to_teacher_{user_id}")]
        for user_id, full_name in teachers
    ])

    await message.answer("Выберите преподавателя из списка:", reply_markup=keyboard)
    await state.set_state(TeacherContact.waiting_for_teacher)


@std.callback_query(lambda c: c.data.startswith("send_to_teacher_"))
async def send_to_teacher(callback_query: CallbackQuery, state: FSMContext):
    teacher_id = int(callback_query.data.split("_")[-1])
    await state.update_data(teacher_id=teacher_id)
    await state.set_state(TeacherContact.waiting_for_message)
    await callback_query.message.answer("Напишите сообщение преподавателю")
    await callback_query.answer()


@std.message(TeacherContact.waiting_for_message)
async def send_message_to_teacher(message: Message, state: FSMContext):
    # Сохраняем сообщение студента в таблицу messages
    data = await state.get_data()
    teacher_id = data.get('teacher_id')
    cur_messages.execute("INSERT INTO messages (user_id, user_type, message) VALUES (?, ?, ?)",
                         (message.from_user.id, 'student', message.text))
    conn_messages.commit()

    # Отправляем сообщение преподавателю
    await send_message_to_teacher(message, teacher_id, 'студент')
    await message.answer("Сообщение успешно отправлено. Ждите ответа.")

    await state.clear()


async def send_message_to_teacher(message: Message, user_id: int, user_type: str):
    await bot.send_message(user_id, f'*Сообщение от {user_type},'
                                    f' {message.from_user.full_name}\n\n*'
                                    f' {message.text}',
                           reply_markup=kb.answer,
                           parse_mode=ParseMode.MARKDOWN)


@std.message(F.text == 'Учебные материалы 📚')
async def cmd_docs(message: Message):
    await message.answer('Учебные документы и шаблоны', reply_markup=kb.docs_panel)


@std.message(F.text == 'Расписание пар 🗓')
async def show_schedule(message: Message):
    schedule = {
        'Понедельник': [
            '1) Математика - Николай И.Н. 301 каб',
            '2) Русский язык - Иванова А.М. 105 каб.',
            '3) Информатика - Лебедев Н.О. 224 каб.',
            '4) Физкультура - Елисеев А.П. 111 каб.'
        ],
        'Вторник': [
            '1) История - Петров С.В. 201 каб.',
            '2) Литература - Сидорова Т.Ю. 105 каб.',
            '3) Физика - Смирнов А.И. 302 каб.',
            '4) Английский язык - Кузнецова М.Н. 107 каб.'
        ],
        'Среда': [
            '1) Химия - Иванов П.П. 303 каб.',
            '2) Биология - Сергеева Е.Д. 304 каб.',
            '3) Обществознание - Соколов Д.В. 202 каб.',
            '4) Технология - Петрова А.С. 106 каб.'
        ],
        'Четверг': [
            '1) Алгебра - Николай И.Н. 301 каб.',
            '2) Геометрия - Николай И.Н. 301 каб.',
            '3) Физкультура - Елисеев А.П. 111 каб.',
            '4) ОБЖ - Смирнов А.И. 302 каб.'
        ],
        'Пятница': [
            '1) Русский язык - Иванова А.М. 105 каб.',
            '2) Литература - Сидорова Т.Ю. 105 каб.',
            '3) Информатика - Лебедев Н.О. 224 каб.',
            '4) Английский язык - Кузнецова М.Н. 107 каб.'
        ]
    }

    schedule_text = '<b>Расписание на неделю:</b>\n\n'
    for day, lessons in schedule.items():
        schedule_text += f'<b>{day}:</b>\n'
        for lesson in lessons:
            schedule_text += f'- {lesson}\n'
        schedule_text += '\n'

    await message.answer(schedule_text, parse_mode=ParseMode.HTML)


@std.message(F.text == 'Меню столовой 🍫')
async def text_menu(message: Message):
    menu = {
        'Понедельник': [
            '1) Борщ со сметаной 🍜 - 250 ккал',
            '2) Макароны с куриной котлетой 🍝 - 450 ккал',
            '3) Компот 🧃 - 100 ккал'
        ],
        'Вторник': [
            '1) Гречневая каша с тушеной говядиной 🍲 - 380 ккал',
            '2) Рыба в кляре с овощами 🐟 - 320 ккал',
            '3) Кисель 🍹 - 80 ккал'
        ],
        'Среда': [
            '1) Суп-лапша с курицей 🍜 - 220 ккал',
            '2) Картофельное пюре с отбивной 🍽️ - 400 ккал',
            '3) Морс 🧃 - 90 ккал'
        ],
        'Четверг': [
            '1) Щи из свежей капусты 🍜 - 180 ккал',
            '2) Рис с тушеной рыбой 🍲 - 350 ккал',
            '3) Кисель 🍹 - 80 ккал'
        ],
        'Пятница': [
            '1) Грибной суп 🍜 - 200 ккал',
            '2) Пельмени с овощным салатом 🥟 - 420 ккал',
            '3) Компот 🧃 - 100 ккал'
        ]
    }

    menu_text = '<b>Меню на неделю:</b>\n\n'
    for day, dishes in menu.items():
        menu_text += f'<b>{day}:</b>\n'
        for dish in dishes:
            menu_text += f'- {dish}\n'
        menu_text += '\n'

    await message.answer(menu_text, parse_mode=ParseMode.HTML)
