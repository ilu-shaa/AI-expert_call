import os
TG_TOKEN = "6656018754:AAEiySDxp4qF-DxZqG-d-Mk2od0k4ljGGBY"
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
 