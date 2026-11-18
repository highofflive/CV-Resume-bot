import os
import telebot
# Завантажує налаштування та секретні дані (паролі, API-ключі) з файлу .env
from dotenv import load_dotenv

# Імпорт ДБ, кнопок, тексту та іншого
from database import CV, SessionLocal, init_db
from keyboards import get_cv_actions_keyboard, get_main_keyboard
from pdf_maker import create_pdf
from texts import HELP_TEXT, SURVEY_STEPS, format_cv_card, format_welcome

load_dotenv()
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# Створення таблиці в базі даних при запуску бота
init_db()

# Тимчасове сховище відповідей під час проходження кроків
user_drafts = {}

# Команда /start
@bot.message_handler(commands=['start'])
def hello(message):
    text = format_welcome(message.from_user.first_name)
    bot.send_message(message.chat.id, text , reply_markup=get_main_keyboard())

# Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        HELP_TEXT,
        parse_mode='html',
        reply_markup=get_main_keyboard()
    )

# - ПОКРОКОВЕ ОПИТУВАННЯ -

@bot.callback_query_handler(func=lambda call: call.data == "start_cv")
def start_cv_flow(call):
    # унікальний номер чату, щоб бот знав, кому саме відповідати.
    chat_id = call.message.chat.id
    user_drafts[chat_id] = {}
    bot.answer_callback_query(call.id)

    msg = bot.send_message(chat_id, SURVEY_STEPS[1], parse_mode='html')
    bot.register_next_step_handler(msg, process_name)

def is_valid_text(message, retry_func) -> bool:
    if not message.text:
        msg = bot.send_message(message.chat.id, "⚠️ Будь ласка, надішли відповідь текстом:")
        bot.register_next_step_handler(msg, retry_func)
        return False

    if message.text.strip() == "/cancel":
        user_drafts.pop(message.chat.id, None)
        bot.send_message(
            message.chat.id,
            "❌ Заповнення скасовано. Повертаю в меню:",
            reply_markup=get_main_keyboard()
        )
        return False

    return True

def process_name(message):
    if not is_valid_text(message, process_name):
        return
    user_drafts[message.chat.id]['name'] = message.text.strip()

    msg = bot.send_message(message.chat.id, SURVEY_STEPS[2], parse_mode='html')
    bot.register_next_step_handler(msg, process_position)

def process_position(message):
    if not is_valid_text(message, process_position):
        return
    user_drafts[message.chat.id]['position'] = message.text.strip()

    msg = bot.send_message(message.chat.id, SURVEY_STEPS[3], parse_mode='html')
    bot.register_next_step_handler(msg, process_contacts)

def process_contacts(message):
    if not is_valid_text(message, process_contacts):
        return
    user_drafts[message.chat.id]['contacts'] = message.text.strip()

    msg = bot.send_message(message.chat.id, SURVEY_STEPS[4], parse_mode='html')
    bot.register_next_step_handler(msg, process_skills)

def process_skills(message):
    if not is_valid_text(message, process_skills):
        return
    user_drafts[message.chat.id]['skills'] = message.text.strip()

    msg = bot.send_message(message.chat.id, SURVEY_STEPS[5], parse_mode='html')
    bot.register_next_step_handler(msg, finish_cv)

def finish_cv(message):
    if not is_valid_text(message, finish_cv):
        return

    chat_id = message.chat.id
    user_drafts[chat_id]['experience'] = message.text.strip()
    draft = user_drafts[chat_id]

    with SessionLocal() as session:
        cv_record = CV(
            chat_id=chat_id,
            name=draft['name'],
            position=draft['position'],
            contacts=draft['contacts'],
            skills=draft['skills'],
            experience=draft['experience']  
        )
        session.merge(cv_record)
        session.commit()
    user_drafts.pop(chat_id, None)

    bot.send_message(
        chat_id,
        "✅ <b>Твоє резюме збережено в базу даних!</b>\nМожеш одразу завантажити готовий PDF-файл:",
        parse_mode='html',
        reply_markup=get_cv_actions_keyboard()
    )

# - ПЕРЕГЛЯД ТА ГЕНЕРАЦІЯ PDF -

@bot.callback_query_handler(func=lambda call: call.data == "view_cv")
def view_saved_cv(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)

    with SessionLocal() as session:
        cv = session.get(CV, chat_id)

    if not cv:
        bot.send_message(
            chat_id,
            "📭 У базі даних ще немає твого резюме. Створи його кнопкою нижче:",
            reply_markup=get_main_keyboard()
        )
        return

    bot.send_message(
        chat_id,
        format_cv_card(cv),
        parse_mode='html',
        reply_markup=get_cv_actions_keyboard()
    )

    
@bot.callback_query_handler(func=lambda call: call.data == "make_pdf")
def send_pdf_cv(call):
    chat_id = call.message.chat.id

    with SessionLocal() as session:
        cv = session.get(CV, chat_id)

    if not cv:
        bot.answer_callback_query(call.id, "Спочатку створи резюме!", show_alert=True)
        return

    bot.answer_callback_query(call.id, 'Генерую PDF...')
    filename = f"CV_{chat_id}.pdf"

    try:
        create_pdf(cv, filename)
        with open(filename, "rb") as pdf_file:
            bot.send_document(
                chat_id,
                pdf_file,
                caption="🎉 Твоє резюме готове! Успіхів на співбесідах."
            )
    finally:
        # Гарантовано видаляємо тимчасовий PDF з диска, навіть якщо під час відправки стався збій
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    print("Бот запустився...")
    bot.infinity_polling()