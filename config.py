from dotenv import load_dotenv
import os
load_dotenv()

ADMIN_ID = int(os.getenv('ADMIN_ID'))
DATA_DIR = os.getenv('DATA_DIR')
TOKEN = os.getenv('TOKEN')
