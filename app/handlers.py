import httpx

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaAudio, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import OPENROUTER_API_KEY

from keyboards.start_keyboard import lang_menu, back_to_start, start_kb
import keyboards.drone_presentation as kb
from static_files.bot_answers import GREETINGS, PRESENTAION_VTOL_DRONES, CERTIFICATE, FEATURES

from workTools.WorkWithDB import WorkWithDB
from workTools.WorkWithTTS import WorkWithTTS
from workTools.WorkWithLLM import MistralAPI
from workTools.WorkWithCache import WorkWithCache

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
    await c.message.edit_text(confirm, reply_markup = await start_kb(chat_lang.get(c.message.chat.id, 'ru')))

@router.callback_query(F.data == 'performance')
@router.callback_query(F.data.startswith("presentaion_"))
async def show_intro(c: CallbackQuery, bot: Bot):
    from new_voice_handler import chat_lang
    cache_key = c.data + chat_lang.get(c.message.chat.id, 'ru') if not c.data == 'performance' else 'presentaion' + chat_lang.get(c.message.chat.id, 'ru')
    check_key = WorkWithCache.check_key(cache_key)
    if check_key:
        print("Данные из кэша")
        print(cache_key)
        audio_bytes, text = WorkWithCache.get_cache(cache_key)
    else:
        print("Данные не из кэша")
        if c.data == 'performance':
            text = await MistralAPI.query(prompt = f"Переведи с русского на {chat_lang.get(c.message.chat.id, 'ru')} {PRESENTAION_VTOL_DRONES}", token = OPENROUTER_API_KEY)
        else:
            text = await MistralAPI.query(prompt = f"Сгенерируй краткое представление дрона (чтобы по размеру вместилось в сообщение в телеграмм) {c.data.split('_')[1]} на {chat_lang.get(c.message.chat.id, 'ru')} языке ", token = OPENROUTER_API_KEY)
        audio_bytes = await WorkWithTTS.text_to_speech(task = cache_key, text = text, lang = chat_lang.get(c.message.chat.id, 'ru'))

    audio = BufferedInputFile(file = audio_bytes, filename = "voice.mp3")

    await bot.edit_message_media(
            chat_id = c.message.chat.id,
            message_id = c.message.message_id,
            media = InputMediaAudio(
                media = audio,
                caption = text
            ),
            reply_markup = await kb.inline_words_phrases() # back_to_start_delete 
        )

@router.callback_query(F.data == 'backStartDelete')
async def back_to_start(c: CallbackQuery):
    from new_voice_handler import chat_lang
    lang = chat_lang[c.message.chat.id]
    confirm = {'ru':'✅ Русский','en':'✅ English','cn':'✅ 中文'}[lang]
    await c.message.delete()
    await c.message.answer(confirm, reply_markup = await start_kb(chat_lang.get(c.message.chat.id, 'ru')))

@router.callback_query(F.data=='features')
async def show_feats(c: CallbackQuery):
    from new_voice_handler import chat_lang
    data = WorkWithDB.show_characteristics('JOUAV CW-15')
    p = data.get('performance', {})
    features = FEATURES[chat_lang.get(c.message.chat.id, 'ru')]
    out = (
        f"🏎️ {features[0][0]} {p.get('max_speed_kmh','?')} {features[0][1]}\n"
        f"⏱️ {features[1][0]} {p.get('flight_time_min','?')} {features[1][1]}\n"
        f"📶 {features[2][0]} {p.get('max_range_km','?')} {features[2][1]}"
    )
    await c.message.answer(out) # reply_markup=back_to_start

@router.callback_query(F.data=='certificate')
async def show_cert(c: CallbackQuery):
    from new_voice_handler import chat_lang
    certificate = CERTIFICATE[chat_lang.get(c.message.chat.id, 'ru')]
    docs = WorkWithDB.show_characteristics('JOUAV CW-15').get('compliance_documents', [])
    await c.message.answer(f'🛂 {certificate}\n' + '\n'.join(docs)) # reply_markup=back_to_start

# Переход в режим Q&A
@router.callback_query(F.data=='question')
async def enter_qa(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.awaiting_question) 
    await c.message.answer('Задайте свой вопрос текстом или голосом.') # reply_markup=back_to_start

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
        best = max(db.items(), key=lambda item: item[1].get('performance', {}).get('max_speed_kmh', 0)) #item: item[1]['performance'].get('max_speed_kmh', 0)
        name, specs = best
        speed = specs['performance']['max_speed_kmh'] 
        await m.answer(f"🚀 Самый быстрый дрон: {name} — {speed} км/ч.") # reply_markup=back_to_start
        return

    # Формируем контекстовую строку
    context = ' '.join(
        # f"{name}: payload {info['weights']['max_payload_kg']}kg, speed {info['performance']['max_speed_kmh']}km/h;"
        f"{name}: payload {info.get('weights', {}).get('max_payload_kg', 'нет данных')}kg, speed {info.get('performance', {}.get('max_speed_kmh', 'нет данных'))}km/h;"
        for name, info in db.items()
    )
    # Запрос к MistralAPI
    prompt = f"Context: {context}\nQuestion: {user_question}"
    answer = await MistralAPI.query(prompt = prompt, token = OPENROUTER_API_KEY)

    await m.answer(f"❓ {user_question}\n\n💬 {answer}") # reply_markup=back_to_start

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
