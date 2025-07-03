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
 
