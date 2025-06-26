import os
import wave
import json
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from app.config import VOSK_MODELS

class Transcriber:
    models = {}

    @staticmethod
    def load_model(lang_code: str):
        path = VOSK_MODELS.get(lang_code)
        if not path or not os.path.isdir(path):
            raise FileNotFoundError(f"Model not found: {path}")
        if lang_code not in Transcriber.models:
            Transcriber.models[lang_code] = Model(path)
        return Transcriber.models[lang_code]

    @staticmethod
    def transcribe(ogg_path: str, lang_code: str) -> str:
        model = Transcriber.load_model(lang_code)
        wav_path = ogg_path.rsplit('.', 1)[0] + '.wav'
        AudioSegment.from_file(ogg_path).export(wav_path, format='wav')

        result = ''
        with wave.open(wav_path, 'rb') as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            while True:
                data = wf.readframes(8000)
                if not data:
                    break
                if rec.AcceptWaveform(data):
                    result += rec.Result() + '\n'
                else:
                    pr = rec.PartialResult()
                    obj = json.loads(pr)
                    txt = obj.get('partial', '')
                    if txt:
                        result += json.dumps({'text': txt}) + '\n'
            result += rec.FinalResult() + '\n'

        os.remove(wav_path)
        return result