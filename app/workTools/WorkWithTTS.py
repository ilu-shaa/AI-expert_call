from gtts import gTTS
from io import BytesIO
import asyncio

from app.workTools.WorkWithCache import WorkWithCache

class WorkWithTTS:
    @staticmethod
    async def text_to_speech(task : str, text: str, lang: str = 'ru') -> BytesIO:
        lang_map = {
            'ru': 'ru',
            'en': 'en',
            'cn': 'zh-CN'
        }

        cache_key = task # task + lang

        def block():
            tts = gTTS(text=text, lang=lang_map.get(lang, 'ru'))
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return mp3_fp.read()

        audio_bytes = await asyncio.to_thread(block)
        if cache_key != "answer-question":
            WorkWithCache.append_cache(cache_key, audio_bytes, text)
        return audio_bytes
