from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from workTools.WorkWithDB import WorkWithDB

async def inline_words_phrases():
    keyboard = InlineKeyboardBuilder()
    db = WorkWithDB.load_all()
    for drone in db.keys():
        keyboard.add(InlineKeyboardButton(text = drone, callback_data = f"presentaion_{drone}"))
    keyboard.add(InlineKeyboardButton(text = "🔙 Назад", callback_data = "backStartDelete"))
    return keyboard.adjust(2).as_markup()