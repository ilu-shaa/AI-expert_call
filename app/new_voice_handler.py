import os
import tempfile
from aiogram import Router
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message
import whisper

# Команды выбора языка
LANG_COMMANDS = {
    'ru': 'lang_ru',
    'en': 'lang_en',
    'cn': 'lang_cn'
}
# Коды языка для whisper
WHISPER_LANG = {
    'ru': 'ru',
    'en': 'en',
    'cn': 'zh'
}

chat_lang = {}
router = Router()

# Кэш модели whisper
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        # используем компактную модель для скорости
        _whisper_model = whisper.load_model('tiny')
    return _whisper_model

# Хендлеры для установки языка
for code, cmd in LANG_COMMANDS.items():
    async def _set_lang(msg: Message, code=code):
        chat_lang[msg.chat.id] = code
        names = {'ru': 'Русский', 'en': 'English', 'cn': '中文'}
        await msg.answer(f"Язык распознавания установлен: {names[code]}")
    router.message(Command(cmd))(_set_lang)

class VoiceFilter(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        return bool(msg.voice)

@router.message(VoiceFilter())
async def voice_handler(msg: Message):
    lang = chat_lang.get(msg.chat.id, 'ru')

    # скачать голосовое сообщение во временный файл
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
        await msg.bot.download(msg.voice.file_id, tmp.name)
        audio_path = tmp.name

    try:
        model = get_whisper_model()
        # транскрипция
        result = model.transcribe(audio_path, language=WHISPER_LANG.get(lang, 'en'))
        text = result.get('text', '').strip()
    except Exception as e:
        text = ''
    finally:
        try:
            os.remove(audio_path)
        except OSError:
            pass

    if not text:
        await msg.answer("❗️ Не удалось распознать речь.")
        return

    # отправка результата
    await msg.answer(f"📝 Распознанный текст ({lang}):\n{text}")
