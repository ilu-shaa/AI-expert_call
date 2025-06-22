import os

TG_TOKEN = "7271971277:AAF5PDe1EBQmELvTjWHFwH3Yd2DTFkJg4xE"

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'static_files', 'db.json')

VOSK_MODELS = {
    'ru': os.path.join(BASE_DIR, 'static_files', 'vosk-model-small-ru-0.22'),
    'en': os.path.join(BASE_DIR, 'static_files', 'vosk-model-en-us-0.22'),
    'cn': os.path.join(BASE_DIR, 'static_files', 'vosk-model-cn-0.22'),
}


MISTRAL_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# API‑ключ для OpenRouter (Mistral)
OPENROUTER_API_KEY  = "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"

# Путь к локальной Llama 2‑13B
USE_LOCAL_QWEN = True
 