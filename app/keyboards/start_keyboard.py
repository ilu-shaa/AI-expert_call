from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Представление продукта", callback_data = 'performance')],
     [InlineKeyboardButton(text="Задать вопрос", callback_data = 'question')],
     [InlineKeyboardButton(text="Сравнение", callback_data = 'compare')],
     [InlineKeyboardButton(text="Озвучить презентацию", callback_data = 'voiceActing')]
])
back_to_start = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data = 'backStart')]])