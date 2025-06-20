from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

lang_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
        InlineKeyboardButton(text="🇨🇳 中文", callback_data="set_lang:cn"),
    ]
])

start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📣 Презентация", callback_data="performance")],
    [InlineKeyboardButton(text="📊 Характеристики", callback_data="features")],
    [InlineKeyboardButton(text="📄 Сертификаты", callback_data="certificate")],
    [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="question")],
    [InlineKeyboardButton(text="🎤 Озвучить свой текст", callback_data="voiceActing")],
])

back_to_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="backStart")]
])

back_to_start_delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="backStartDelete")]
])
