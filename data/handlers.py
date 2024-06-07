import asyncio
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, Command, CommandObject, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
import data.keyboards as kb
import openpyxl

hand = Router()


@hand.message(CommandStart())
async def cmd_start(message: Message):
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(1)
    sticker = ('CAACAgIAAxkBAAJY-2ZO6Z8uCCJFRtNa-'
               'GxqthLHlooZAAKQFQACtOXJS8_bwAcOv4PpNQQ')
    await message.answer_sticker(sticker)
    await message.answer(f'Здраствуйте {message.from_user.username}!'
                         f' Вы находитесь в главном меню ЭнергоБота.',
                         reply_markup=kb.main)


@hand.message(Command('check_list'))
async def cmd_table(message: Message):
    book = openpyxl.open(r".\app\docs\data.xlsx", read_only=True)
    sheet = book.active

    output = ""

    for row in sheet.iter_rows(min_row=1, values_only=True):
        row_values = []
        for cell in row:
            if cell is not None and cell != "":
                row_values.append(str(cell))
        if row_values:
            output += "| " + " | ".join(row_values) + " |\n"

    if output:
        parts = [output[i:i + 2000] for i in range(0, len(output), 2000)]  # разбиваем строку
                                                                           # на части по
                                                                           # 2000 символов
        for part in parts:
            await message.answer("```\n" + part + "```")  # отправляем каждую часть отдельно
    else:
        await message.answer("Таблица пуста или не содержит заполненных ячеек.")


@hand.message(F.text == 'Назад')
async def cmd_start_back(message: Message):
    await cmd_start(message)


@hand.message(F.text == 'Узнать о боте')
async def cmd_about(message: Message):
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(1)
    await message.reply(f'Приветствую, {message.from_user.full_name}, я '
                        f'ЭнергоБот, созданный для помощи между студентами и '
                        f'преподавателями. Я еще в разработке. Если вы '
                        f'студент или преподаватель, вы можете зайти в '
                        f'личный кабинет, однако если не выходит, '
                        f'обратитесь к вашему куратору.')


@hand.message(F.text == 'Сайт колледжа')
async def cmd_site(message: Message):
    await message.answer_photo(photo='https://lh3.googleusercontent.com'
                                     '/p/AF1QipM8MkG4sv0a2Fk-hQYESG-H3A'
                                     '5rmjC9Y68GLEhi=w600-k')
    await message.answer('Сайт энергетического колледжа', reply_markup=kb.site)


@hand.message(F.text == 'Новости колледжа')
async def cmd_group(message: Message):
    await message.answer_photo(photo='https://proverili.ru/uploads/media/'
                                     '5236/1.jpg')
    await message.answer('Канал колледжа', reply_markup=kb.group)
