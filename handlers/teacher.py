from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import handlers.keyboards as kb
from config import TOKEN, STUDENT_ID

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


class WorkTest(StatesGroup):
    quest1 = State()
    q1_answer1 = State()
    q1_answer2 = State()
    q1_answer3 = State()
    q1_answer4 = State()


@teach.message(F.text == 'Создать тест')
async def text_create_test(message: Message, state: FSMContext):
    await state.set_state(WorkTest.quest1)
    await message.answer('Напишите первый вопрос', reply_markup=kb.cancel)


@teach.message(F.text == 'Выйти из создания теста')
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'<b>Создание теста прекращено</b>', parse_mode=ParseMode.HTML,
                         reply_markup=kb.teacher_panel())


@teach.message(WorkTest.quest1)
async def test_q1_answer1(message: Message, state: FSMContext):
    await state.update_data(quest1=message.text)
    await state.set_state(WorkTest.q1_answer1)
    await message.answer('Напишите первый вариант ответа')


@teach.message(WorkTest.q1_answer1)
async def test_q1_answer1(message: Message, state: FSMContext):
    await state.update_data(q1_answer1=message.text)
    await state.set_state(WorkTest.q1_answer2)
    await message.answer('Далее напишите второй вариант ответа')


@teach.message(WorkTest.q1_answer2)
async def test_q1_answer2(message: Message, state: FSMContext):
    await state.update_data(q1_answre2=message.text)
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

    formated_text = []
    [
        formated_text.append(f'{key}: {value}')
        for key, value in data.items()
    ]
    await message.answer('Обзор теста:')
    await message.answer(
        "\n.".join(f'`{formated_text}`'),
        parse_mode=ParseMode.MARKDOWN
    )
