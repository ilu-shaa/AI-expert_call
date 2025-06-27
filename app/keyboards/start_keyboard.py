from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Меню выбора языка
lang_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
        InlineKeyboardButton(text="🇨🇳 中文", callback_data="set_lang:cn"),
    ]
])

# Кнопки стартового меню для каждого языка
start_buttons = {
    "ru": [
        "📣 Презентация",
        "📊 Характеристики",
        "🔄 Сравнить",
        "❓ Задать вопрос"
    ],
    "en": [
        "📣 Presentation",
        "📊 Characteristics",
        "🔄 Compare",
        "❓ Ask a question"
    ],
    "cn": [
        "📣 推介會",
        "📊 特徵",
        "🔄 比較",
        "❓ 問一個問題"
    ]
}

# callback_data для соответствующих кнопок
start_callback = [
    "performance",
    "features",
    "compare",        # новая кнопка для компаратора
    "question"
]

# Генерация стартовой клавиатуры в зависимости от языка
async def start_kb(language: str):
    keyboard = InlineKeyboardBuilder()
    for i in range(len(start_buttons[language])):
        keyboard.add(InlineKeyboardButton(
            text=start_buttons[language][i],
            callback_data=start_callback[i]
        ))
    return keyboard.adjust(1).as_markup()

# Кнопка "Назад" (без удаления)
back_to_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="backStart")]
])

# Кнопка "Назад" (с удалением)
back_to_start_delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="backStartDelete")]
])
