from aiogram.fsm.state import State, StatesGroup


# Связь с преподавателем со стороны студента

# Стэйты для тестов
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
    quest4 = State()
    q4_answer1 = State()
    q4_answer2 = State()
    q4_answer3 = State()
    q4_answer4 = State()
    quest5 = State()
    q5_answer1 = State()
    q5_answer2 = State()
    q5_answer3 = State()
    q5_answer4 = State()


# Вызов админа преподавателю
class AdminCall(StatesGroup):
    wait_to_message = State()


class StudentMessage(StatesGroup):
    waiting_for_message = State()
    waiting_for_response1 = State()
    waiting_for_teacher = State()


# Ответ на сообщение студенту
class TeacherMessage(StatesGroup):
    waiting_for_message = State()
    waiting_for_student = State()
    waiting_for_response = State()
