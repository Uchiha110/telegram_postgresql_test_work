import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')
GIGA_CHAD_API_KEY = os.getenv('GIGA_CHAD_API_KEY')
bot = Bot(token=TOKEN)
