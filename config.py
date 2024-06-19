import pathlib

from aiogram import Bot
from dotenv import load_dotenv
import os
load_dotenv()

ADMIN_ID = int(os.getenv('ADMIN_ID'))
DATA_DIR = pathlib.Path(os.getenv('DATA_DIR'))
TOKEN = os.getenv('TOKEN')
STUDENT_ID = int(os.getenv('STUDENT_ID'))
TEACHER_ID = int(os.getenv('TEACHER_ID'))
bot = Bot(token=TOKEN)