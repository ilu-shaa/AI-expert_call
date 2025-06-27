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

from app.config import OPENROUTER_API_KEY
from app.keyboards.start_keyboard import lang_menu, start_kb, back_to_start
from app.static_files.bot_answers import GREETINGS, CERTIFICATE
from app.new_voice_handler import chat_lang, WHISPER_LANG
from app.workTools.WorkWithDB import WorkWithDB
from app.workTools.WorkWithTTS import WorkWithTTS
from app.workTools.WorkWithLLM import MistralAPI
from app.workTools.WorkWithCache import WorkWithCache
from app.workTools.search_db import search_db

# FSM states
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
# /start and language selection
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
    names = list(WorkWithDB.load_all().keys())
    buttons = [InlineKeyboardButton(text=n, callback_data=f"feat:{n}") for n in names]
    kb = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
    await c.message.answer("Выберите модель для просмотра характеристик:", reply_markup=kb)

@router.callback_query(F.data.startswith('feat:'))
async def show_features(c: CallbackQuery):
    name = c.data.split(':',1)[1]
    specs = WorkWithDB.show_characteristics(name)
    lines = [f"📌 <b>{name}</b>"]
    for section in ("performance", "weights", "dimensions"):
        data = specs.get(section, {})
        if data:
            lines.append(f"\n<b>{section.title()}:</b>")
            for k,v in data.items():
                lines.append(f"• {k}: {v}")
    docs = specs.get("compliance_documents", [])
    if docs:
        lines.append("\n<b>Документы соответствия:</b>")
        for d in docs:
            lines.append(f"• {d}")

    await c.message.answer("\n".join(lines), parse_mode="HTML")

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

    relevant = search_db(user_question, top_k=2)
    context = "\n\n".join([f"{name}:\n{info}" for name, info in relevant])
    system_prompt = {
        'ru': "Ты — эксперт по VTOL-дронам. Используй только приведённую информацию для ответа.",
        'en': "You are a VTOL drone expert. Use only the provided context to answer.",
        'cn': "您是 VTOL 无人机专家。仅使用以下信息进行回答。"
    }[lang]

    prompt = f"{system_prompt}\n\nКонтекст:\n{context}\n\nВопрос: {user_question}"

    answer = await MistralAPI.query(prompt=prompt, system=system_prompt, max_tokens=200)
    answer = answer.strip()
    if len(answer) > 1000:
        answer = answer[:997] + "..."

    await m.answer(answer)
    audio = await WorkWithTTS.text_to_speech(task="answer-question", text=answer, lang=lang)
    await m.answer_audio(BufferedInputFile(audio, filename="answer.mp3"))
# -------------------
# Comparator multi-select
# -------------------
@router.callback_query(F.data == 'compare')
async def ask_compare(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.awaiting_compare_selection)
    await state.update_data(compare_list=[])
    await send_compare_keyboard(c, state)

async def send_compare_keyboard(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen = set(data.get('compare_list', []))
    names = list(WorkWithDB.load_all().keys())
    buttons = []
    for n in names:
        mark = '✅' if n in chosen else '▫️'
        buttons.append(InlineKeyboardButton(text=f"{mark} {n}", callback_data=f"toggle:{n}"))
    buttons.append(InlineKeyboardButton(text="🔀 Сравнить", callback_data="run_compare"))
    kb = InlineKeyboardMarkup(inline_keyboard=[buttons[i:i+2] for i in range(0, len(buttons), 2)])
    try:
        await c.message.edit_text('Выберите модели для сравнения:', reply_markup=kb)
    except:
        await c.message.answer('Выберите модели для сравнения:', reply_markup=kb)

@router.callback_query(F.data.startswith('toggle:'))
async def toggle_model(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosen = set(data.get('compare_list', []))
    m = c.data.split(':', 1)[1]
    if m in chosen:
        chosen.remove(m)
    else:
        chosen.add(m)
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
        'ru': 'Вы — эксперт. Ответьте очень кратко на русском без тегов.',
        'en': 'You are an expert. Answer very concisely in English without tags.',
        'cn': '您是專家，請非常簡短地回答，不要使用標籤。'
    }[lang]
    user_msg = f"Сравните эти дроны по ключевым параметрам: {content}"
    try:
        resp = ollama.chat(
            model='qwen3:8b',
            messages=[
                {'role': 'system', 'content': system_msg},
                {'role': 'user', 'content': user_msg}
            ]
        )
        report = resp['message']['content']
    except Exception as e:
        report = f"❌ Ошибка при сравнении: {e}"
    # Удаляем любые теги
    report = re.sub(r'<[^>]+>', '', report).strip()
    await c.message.answer(report, parse_mode=None)
    audio = await WorkWithTTS.text_to_speech(task='compare', text=report, lang=lang)
    await c.message.answer_audio(BufferedInputFile(audio, filename='compare.mp3'))
    await state.clear()