import telebot
import os
from dotenv import load_dotenv
from telebot import types

# Імпортуємо модель таблиці, фабрику сесій та функцію створення БД із нашого файлу database.py
from database import CV, SessionLocal, init_db

# Імпортуємо кнопки
from keyboards import get_main_keyboard

# Завантажуємо змінні з .env та створюємо об'єкт бота
load_dotenv()
token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)

# Ініціалізуємо базу даних при старті бота
init_db()

# Тимчасовий словник для зберігання відповідей, поки юзер проходить опитування
user_drafts = {}

#Команда /start
@bot.message_handler(commands=['start'])
def hello(message):
    text = f"""Привіт! {message.from_user.first_name}👋 Я твій кар'єрний асистент. Допоможу створити стильне та структуроване резюме всього за 5 хвилин.\n
Що ми зробимо разом:
🔹 Зберемо твій досвід та навички в чітку систему.
🔹 Підберемо правильні формулювання для рекрутерів.
🔹 Згенеруємо готовий PDF-файл, який одразу можна надсилати роботодавцям.

Готовий розпочати? Тисни /help , та дізнайся як правильно створювати резюме
    """
    bot.send_message(message.chat.id, text)


#Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    text = """<b>Як створити своє перше резюме?</b>

Зі мною ти швидко збереш структуроване та професійне CV без зайвого головного болю. Просто відповідай на мої запитання, а я оформлю все в готовий документ.

<b>Що я вмію (основні команди):</b>
🔹 /start — створити нове резюме з нуля
🔹 /help — Як створити резюме?

💡 <b>Порада:</b> Намагайся описувати свій досвід через конкретні досягнення та цифри — це привертає найбільше уваги!"""

    bot.send_message(message.chat.id, text, parse_mode='html')


print("Бот запустився...")
bot.polling(none_stop=True)