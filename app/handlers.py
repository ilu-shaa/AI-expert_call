import json
import os
import tempfile
import re
import whisper
import ollama
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, BufferedInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import OPENROUTER_API_KEY
from keyboards.start_keyboard import lang_menu, start_kb, back_to_start
from static_files.bot_answers import GREETINGS
from new_voice_handler import chat_lang, WHISPER_LANG
from workTools.WorkWithDB import WorkWithDB
from workTools.WorkWithTTS import WorkWithTTS
from workTools.WorkWithLLM import MistralAPI
from workTools.WorkWithCache import WorkWithCache
from workTools.search_db import search_db


class Flag(StatesGroup):
    awaiting_question = State()
    awaiting_tts_text = State()
    awaiting_compare_selection = State()

router = Router()
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model('tiny')
    return _whisper_model

# -------------------
# /start
# -------------------
@router.message(Command('start'))
async def cmd_start(msg: Message):
    chat_lang.pop(msg.chat.id, None)
    await msg.answer(GREETINGS, reply_markup=lang_menu)

@router.callback_query(F.data.startswith('set_lang:'))
async def set_lang(c: CallbackQuery):
    lang = c.data.split(':', 1)[1]
    chat_lang[c.message.chat.id] = lang
    confirm = {'ru': '✅ Русский', 'en': '✅ English', 'cn': '✅ 中文'}[lang]
    await c.message.edit_text(confirm, reply_markup=await start_kb(lang))

# -------------------
# Презентация / Комплектация
# -------------------
@router.callback_query(F.data == 'performance')
@router.callback_query(F.data.startswith('presentaion_'))
async def show_intro(c: CallbackQuery):
    lang = chat_lang.get(c.message.chat.id, 'ru')
    key = f"{c.data}_{lang}"
    if WorkWithCache.check_key(key):
        audio_bytes, text = WorkWithCache.get_cache(key)
    else:
        drone = c.data.split('_', 1)[1] if c.data != 'performance' else ''
        template = {
            'ru': f"Сократите до 2 предложений описание VTOL-дронов {drone}",
            'en': f"Summarize in 2 sentences a description of VTOL drones {drone}",
            'cn': f"用2句话简要描述VTOL无人机 {drone}"
        }[lang]
        text = await MistralAPI.query(prompt=template, system=template, max_tokens=100)
        audio_bytes = await WorkWithTTS.text_to_speech(task=key, text=text, lang=lang)
        WorkWithCache.append_cache(key, audio_bytes, text)
    await c.message.answer(text)
    await c.message.answer_audio(BufferedInputFile(audio_bytes, filename='intro.mp3'))
# -------------------
# Характеристики: список дронов и выбор модели
# -------------------
@router.callback_query(F.data == 'features')
async def features_list(c: CallbackQuery):
    lang = chat_lang.get(c.message.chat.id, 'ru')
    prompt = {'ru': 'Выберите модель...', 'en': 'Select a model...', 'cn': '请选择型号...'}[lang]
    names = list(WorkWithDB.load_all().keys())
    buttons = [InlineKeyboardButton(text=n, callback_data=f'feat:{n}') for n in names]
    kb = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
    await c.message.answer(prompt, reply_markup=kb)

@router.callback_query(F.data.startswith('feat:'))
async def show_features(c: CallbackQuery):
    name = c.data.split(':', 1)[1]
    lang = chat_lang.get(c.message.chat.id, 'ru')
    specs = WorkWithDB.show_characteristics(name)
    context = json.dumps(specs, ensure_ascii=False, indent=2)
    prompt = {
        'ru': f"Ты — эксперт по дронам. Сократите до 2 предложений описание VTOL-дронов {name} на русском языке: {context}",
        'en': f"You are a drone expert. Generate a very brief introduction to the drone (only the main characteristics) {name} in English: {context}",
        'cn': f"您是无人机专家。將垂直起降無人機的描述縮減為 2 句話 {name} 的特性: {context}"
    }[lang]
    result = await MistralAPI.query(prompt=prompt, system=prompt, max_tokens=500)
    await c.message.answer(result)

# -------------------
# Вход в Q&A
# -------------------
@router.callback_query(F.data == 'question')
async def enter_qa(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.awaiting_question)
    lang = chat_lang.get(c.message.chat.id, 'ru')
    prompt_text = {
        'ru': '❓ Задайте вопрос текстом или отправьте голосовое сообщение.',
        'en': '❓ Ask your question by text or send a voice message.',
        'cn': '❓ 请以文字提问或发送语音消息。'
    }[lang]
    await c.message.answer(prompt_text)

@router.message(Flag.awaiting_question)
async def handle_question(m: Message, state: FSMContext):
    await state.clear()
    lang = chat_lang.get(m.chat.id, 'ru')

    if m.voice:
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            await m.bot.download(m.voice.file_id, tmp.name)
            audio_path = tmp.name
        try:
            res = get_whisper_model().transcribe(audio_path, language=WHISPER_LANG.get(lang, 'en'))
            user_question = res.get('text', '').strip()
        except:
            user_question = ''
        finally:
            try: os.remove(audio_path)
            except: pass

        if not user_question:
            return await m.answer({
                'ru': "❗️ Не удалось распознать речь.",
                'en': "❗️ Could not transcribe audio.",
                'cn': "❗️ 无法识别语音。"
            }[lang])
    else:
        user_question = m.text or ""

    # Загружаем всю базу без ограничений
    full_db = WorkWithDB.load_all()
    context = "\n\n".join([f"{name}:\n{info}" for name, info in full_db.items()])

    system_prompt = {
        'ru': "Ты — эксперт по VTOL-дронам. Используй только приведённую информацию для ответа.",
        'en': "You are a VTOL drone expert. Use only the provided context to answer.",
        'cn': "您是 VTOL 无人机专家。仅使用以下信息进行回答。"
    }[lang]

    prompt = f"{system_prompt}\n\nКонтекст:\n{context}\n\nВопрос: {user_question}"

    answer = await MistralAPI.query(prompt=prompt, system=system_prompt, max_tokens=1000)
    answer = answer.strip()
    if len(answer) > 1000:
        answer = answer[:997] + "..."

    await m.answer(answer)
    audio = await WorkWithTTS.text_to_speech(task="answer-question", text=answer, lang=lang)
    await m.answer_audio(BufferedInputFile(audio, filename="answer.mp3"))


# -------------------
# Компаратор
# -------------------

@router.callback_query(F.data == 'compare')
async def ask_compare(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.awaiting_compare_selection)
    lang = chat_lang.get(c.message.chat.id, 'ru')
    await state.update_data(compare_list=[], lang=lang)
    await send_compare_keyboard(c, state)

async def send_compare_keyboard(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen = set(data.get('compare_list', []))
    lang = data.get('lang', 'ru')
    labels = {'ru': 'Сравнить', 'en': 'Compare', 'cn': '比较'}
    prompt = {'ru': 'Выберите модели:', 'en': 'Select drones:', 'cn': '选择无人机:'}[lang]
    names = list(WorkWithDB.load_all().keys())
    buttons = [InlineKeyboardButton(text=('✅ ' if n in chosen else '▫️ ')+n, callback_data=f"toggle:{n}") for n in names]
    buttons.append(InlineKeyboardButton(text=f"🔀 {labels[lang]}", callback_data='run_compare'))
    kb = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
    try:
        await c.message.edit_text(prompt, reply_markup=kb)
    except:
        await c.message.answer(prompt, reply_markup=kb)

@router.callback_query(F.data.startswith('toggle:'))
async def toggle_model(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen = set(data['compare_list'])
    model = c.data.split(':',1)[1]
    chosen.symmetric_difference_update({model})
    await state.update_data(compare_list=list(chosen))
    await send_compare_keyboard(c, state)

@router.callback_query(F.data == 'run_compare')
async def run_compare(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen = data.get('compare_list', [])
    if len(chosen) < 2:
        return await c.message.answer('Выберите минимум 2 дрона.')
    db = WorkWithDB.load_all()
    pairs = [f"{n}: {json.dumps(db[n], ensure_ascii=False)}" for n in chosen]
    content = ' ; '.join(pairs)
    lang = chat_lang.get(c.message.chat.id, 'ru')
    system_msg = {
        'ru': 'Ты — эксперт по БАС. Ответь ОЧЕНЬ кратко и по сути, ТОЛЬКО ГЛАВНОЕ, БЕЗ ТАБЛИЦ ФОРМАТ ОТЧЕТА, КОЛИЧЕСТВО СИМВОЛОВ ОГРАНИЧЕНО, 3 ПРЕДЛОЖЕНИЯ, строго на русском языке.',
        'en': 'You are a drone expert. Answer VERY briefly and to the point, ONLY THE MAIN, NUMBER OF CHARACTERS IS LIMITED, 3 SENTENCES in English.',
        'cn': '您是無人機專家。請用三句話簡短回答這個問題。 嚴格用中文回答'
    }[lang]
    user_msg = {
        'ru': f"Сравни модели по ключевым характеристикам: {content}",
        'en': f"Compare the drones based on key specifications: {content}",
        'cn': f"请比较以下无人机的主要参数: {content}"
    }[lang]

    try:
        report = await MistralAPI.query(prompt=user_msg, system=system_msg, max_tokens=1000)
    except Exception as e:
        report = f"❌ Ошибка при сравнении: {e}"
    report = re.sub(r'<[^>]+>', '', report).strip()
    await c.message.answer(report, parse_mode=None)
    audio = await WorkWithTTS.text_to_speech(task='compare', text=report, lang=lang)
    await c.message.answer_audio(BufferedInputFile(audio, filename='compare.mp3'))
    await state.clear()
