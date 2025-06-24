from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


lang_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
        InlineKeyboardButton(text="🇨🇳 中文", callback_data="set_lang:cn"),
    ]
])

start_buttons = {"ru" : ["📣 Презентация", "📊 Характеристики", "📄 Сертификаты", "❓ Задать вопрос"],
                 "en" : ["📣 Presentation", "📊 Characteristic", "📄 Certificates", "❓ Ask a question"],
                 "cn" : ["📣 推介會", "📊 特徵", "📄 證書", "❓ 問一個問題"]}

start_callback = ["performance", "features", "certificate", "question"]

async def start_kb(language: str):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(start_buttons[language])):
        keyboard.add(InlineKeyboardButton(text = start_buttons[language][i], callback_data = start_callback[i]))
    return keyboard.adjust(1).as_markup()

back_to_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="backStart")]
])

back_to_start_delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="backStartDelete")]
])
