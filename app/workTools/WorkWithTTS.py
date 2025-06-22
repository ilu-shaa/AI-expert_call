from gtts import gTTS
from io import BytesIO
import asyncio

class WorkWithTTS:
    @staticmethod
    async def text_to_speech(text: str, lang: str = 'ru') -> BytesIO:
        lang_map = {
            'ru': 'ru',
            'en': 'en',
            'cn': 'zh-CN'
        }

        def block():
            tts = gTTS(text=text, lang=lang_map.get(lang, 'ru'))
            mp3_fp = BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return mp3_fp.read()

        audio_bytes = await asyncio.to_thread(block)
        return audio_bytes
