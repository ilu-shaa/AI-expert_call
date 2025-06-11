from gtts import gTTS

class WorkWithTTS:
    @staticmethod
    def text_to_speech(text: str, language: str) -> gTTS:
        voice = gTTS(text = text, lang = language, slow = False)
        return voice