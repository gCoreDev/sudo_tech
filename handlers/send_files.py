from aiogram import F, Router
from aiogram.types.input_file import FSInputFile
from aiogram.types import CallbackQuery

from config import DATA_DIR

file = Router()


@file.callback_query(F.data == 'Ref')
async def send_file(callback: CallbackQuery):
    doc = FSInputFile(DATA_DIR / 'docs/Doclad.docx',
                      'Доклад.docx')
    await callback.answer('Файл получен')
    await callback.message.delete_reply_markup()
    await callback.message.delete()
    await callback.message.answer_document(doc)


@file.callback_query(F.data == 'Kur')
async def send_file(callback: CallbackQuery):
    doc = FSInputFile(DATA_DIR / 'docs/Kursovaya.docx',
                      'Курсовая.docx')
    await callback.answer('Файл получен')
    await callback.message.delete_reply_markup()
    await callback.message.delete()
    await callback.message.answer_document(doc)


@file.callback_query(F.data == 'Otc')
async def send_file(callback: CallbackQuery):
    doc = FSInputFile(DATA_DIR / 'docs/Practica.docx',
                      'Отчет по практике.docx')
    await callback.answer('Файл получен')
    await callback.message.delete_reply_markup()
    await callback.message.delete()
    await callback.message.answer_document(doc)


@file.callback_query(F.data == 'Dip')
async def send_file(callback: CallbackQuery):
    doc = FSInputFile(DATA_DIR / 'docs/Diplom.docx',
                      'Дипломная работа.docx')
    await callback.answer('Файл получен')
    await callback.message.delete_reply_markup()
    await callback.message.delete()
    await callback.message.answer_document(doc)


@file.callback_query(F.data == 'Gos')
async def send_file(callback: CallbackQuery):
    doc = FSInputFile(DATA_DIR / 'docs/Gost.pdf',
                      'Оформление документа.docx')
    await callback.answer('Файл получен')
    await callback.message.delete_reply_markup()
    await callback.message.delete()
    await callback.message.answer_document(doc)
