from telebot import types

# Головне меню бота.
def get_main_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_create = types.InlineKeyboardButton(
        text="🚀 Створити / оновити резюме",
        callback_data="start_cv"
    )
    btn_view = types.InlineKeyboardButton(
        text="📋 Переглянути моє резюме",
        callback_data="view_cv"
    )
    markup.add(btn_create, btn_view)
    return markup

# Кнопки дій під переглядом збереженого резюме.
def get_cv_actions_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_pdf = types.InlineKeyboardButton(
        text="📥 Завантажити PDF",
        callback_data="make_pdf"
    )
    btn_refill = types.InlineKeyboardButton(
        text="🔄 Заповнити заново",
        callback_data="start_cv"
    )
    markup.add(btn_pdf, btn_refill)
    return markup