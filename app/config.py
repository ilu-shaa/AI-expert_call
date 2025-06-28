import os
TG_TOKEN = "7975418794:AAGHW16adTdJ-uyU6HPg6Y1sgCn_IJAW94E"
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'static_files', 'db.json')
VOSK_MODELS = {
    'ru': os.path.join(BASE_DIR, 'static_files', 'vosk-model-small-ru-0.22'),
    'en': os.path.join(BASE_DIR, 'static_files', 'vosk-model-en-us-0.22'),
    'cn': os.path.join(BASE_DIR, 'static_files', 'vosk-model-cn-0.22'),
}
MISTRAL_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY  = "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"
USE_LOCAL_QWEN = True
 
