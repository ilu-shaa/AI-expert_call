from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import app.keyboards.start_keyboard as kb
from app.static_files.bot_answers import GREETINGS
from app.workTools.WorkWithDB import WorkWithDB
from app.workTools.WorkWithTTS import WorkWithTTS

class Flag(StatesGroup):
    presentation_text = State()
    qa_text = State()

router = Router()

@router.message(Command('start'))
async def cmd_start(msg: Message):
    from app.new_voice_handler import chat_lang
    chat_lang.pop(msg.chat.id, None)
    await msg.answer(GREETINGS, reply_markup=kb.lang_menu)

@router.callback_query(F.data.startswith('set_lang:'))
async def set_lang(c: CallbackQuery):
    from app.new_voice_handler import chat_lang
    lang = c.data.split(':')[1]
    chat_lang[c.message.chat.id] = lang
    confirm = {'ru':'✅ Русский','en':'✅ English','cn':'✅ 中文'}[lang]
    await c.message.edit_text(confirm, reply_markup=kb.start)

@router.callback_query(F.data == 'performance')
async def show_intro(c: CallbackQuery):
    from app.new_voice_handler import chat_lang
    text = 'Добрый день! Я ваш ИИ‑ассистент по VTOL‑дронам. Вот презентация продукта CW-15.'
    audio = WorkWithTTS.text_to_speech(text, chat_lang.get(c.message.chat.id, 'ru'))
    await c.message.answer_audio(audio=audio)
    await c.message.answer(text, reply_markup=kb.back_to_start)

@router.callback_query(F.data == 'features')
async def show_feats(c: CallbackQuery):
    data = WorkWithDB.show_characteristics('JOUAV CW-15')
    p = data.get('performance', {})
    out = (
        f"🏎️ Скорость: {p.get('max_speed_kmh','?')} км/ч\n"
        f"⏱️ Время полёта: {p.get('flight_time_min','?')} мин\n"
        f"📶 Радиус: {p.get('max_range_km','?')} км"
    )
    await c.message.answer(out, reply_markup=kb.back_to_start)

@router.callback_query(F.data == 'certificate')
async def show_cert(c: CallbackQuery):
    docs = WorkWithDB.show_characteristics('JOUAV CW-15').get('compliance_documents', [])
    await c.message.answer('🛂 Сертификаты и документы:\n' + '\n'.join(docs), reply_markup=kb.back_to_start)

@router.callback_query(F.data == 'question')
async def ask_qa(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.qa_text)
    await c.message.answer('❓ Задайте свой вопрос текстом или голосом.', reply_markup=kb.back_to_start)

@router.message(Flag.qa_text)
async def handle_qa(m: Message, state: FSMContext):
    from app.new_voice_handler import chat_lang
    lang = chat_lang.get(m.chat.id, 'ru')
    await state.clear()
    answer = f"Вы спросили: {m.text}\n(здесь будет ответ LLM)"
    await m.answer(answer, reply_markup=kb.start)

@router.callback_query(F.data == 'voiceActing')
async def ask_tts(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.presentation_text)
    await c.message.answer('✍️ Напишите текст для озвучки.', reply_markup=kb.back_to_start)

@router.message(Flag.presentation_text)
async def gen_tts(m: Message, state: FSMContext):
    from app.new_voice_handler import chat_lang
    text = m.text or ''
    await state.clear()
    audio = WorkWithTTS.text_to_speech(text, chat_lang.get(m.chat.id, 'ru'))
    await m.answer_audio(audio=audio)
    await m.answer(GREETINGS, reply_markup=kb.start)
