
import httpx
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.start_keyboard import lang_menu, start, back_to_start
from static_files.bot_answers import GREETINGS
from workTools.WorkWithDB import WorkWithDB
from workTools.WorkWithTTS import WorkWithTTS
from workTools.WorkWithLLM import MistralAPI

# FSM состояния
class Flag(StatesGroup):
    awaiting_question = State()
    awaiting_tts_text = State()

router = Router()

@router.message(Command('start'))
async def cmd_start(msg: Message):
    from new_voice_handler import chat_lang
    chat_lang.pop(msg.chat.id, None)
    await msg.answer(GREETINGS, reply_markup=lang_menu)

@router.callback_query(F.data.startswith('set_lang:'))
async def set_lang(c: CallbackQuery):
    from new_voice_handler import chat_lang
    lang = c.data.split(':')[1]
    chat_lang[c.message.chat.id] = lang
    confirm = {'ru':'✅ Русский','en':'✅ English','cn':'✅ 中文'}[lang]
    await c.message.edit_text(confirm, reply_markup=start)

@router.callback_query(F.data=='performance')
async def show_intro(c: CallbackQuery):
    from new_voice_handler import chat_lang
    text = 'Добрый день! Я ваш ИИ‑ассистент по VTOL‑дронам. Вот презентация продукта.'
    audio = WorkWithTTS.text_to_speech(text, chat_lang.get(c.message.chat.id, 'ru'))
    await c.message.answer_audio(audio=audio)
    await c.message.answer(text, reply_markup=back_to_start)

@router.callback_query(F.data=='features')
async def show_feats(c: CallbackQuery):
    data = WorkWithDB.show_characteristics('JOUAV CW-15')
    p = data.get('performance', {})
    out = (
        f"🏎️ Скорость: {p.get('max_speed_kmh','?')} км/ч\n"
        f"⏱️ Время полёта: {p.get('flight_time_min','?')} мин\n"
        f"📶 Радиус: {p.get('max_range_km','?')} км"
    )
    await c.message.answer(out, reply_markup=back_to_start)

@router.callback_query(F.data=='certificate')
async def show_cert(c: CallbackQuery):
    docs = WorkWithDB.show_characteristics('JOUAV CW-15').get('compliance_documents', [])
    await c.message.answer('🛂 Сертификаты и документы:\n' + '\n'.join(docs), reply_markup=back_to_start)

# Переход в режим Q&A
@router.callback_query(F.data=='question')
async def enter_qa(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.awaiting_question)
    await c.message.answer('❓ Задайте свой вопрос текстом или голосом.', reply_markup=back_to_start)

# Обработка вопроса только через MistralAPI
@router.message(Flag.awaiting_question)
async def handle_question(m: Message, state: FSMContext):
    await state.clear()
    user_question = m.text.strip()

    # Загружаем весь контекст из БД
    db = WorkWithDB.load_all()  # вернёт dict {name: specs}
    
    # Простая локальная проверка суперлативов
    uq = user_question.lower()
    if 'самый быстрый' in uq:
        best = max(db.items(), key=lambda item: item[1]['performance'].get('max_speed_kmh', 0))
        name, specs = best
        speed = specs['performance']['max_speed_kmh']
        await m.answer(f"🚀 Самый быстрый дрон: {name} — {speed} км/ч.", reply_markup=back_to_start)
        return

    # Формируем контекстовую строку
    context = ' '.join(
        f"{name}: payload {info['weights']['max_payload_kg']}kg, speed {info['performance']['max_speed_kmh']}km/h;"
        for name, info in db.items()
    )
    # Запрос к MistralAPI
    prompt = f"Context: {context}\nQuestion: {user_question}"
    answer = await MistralAPI.query(prompt)

    await m.answer(f"❓ {user_question}\n\n💬 {answer}", reply_markup=back_to_start)

# Озвучка произвольного текста
@router.callback_query(F.data=='voiceActing')
async def ask_tts(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.awaiting_tts_text)
    await c.message.answer('✍️ Напишите текст для озвучки.', reply_markup=back_to_start)

@router.message(Flag.awaiting_tts_text)
async def gen_tts(m: Message, state: FSMContext):
    from new_voice_handler import chat_lang
    text = m.text or ''
    await state.clear()
    audio = WorkWithTTS.text_to_speech(text, chat_lang.get(m.chat.id, 'ru'))
    await m.answer_audio(audio=audio, reply_markup=back_to_start)
