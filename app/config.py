import os

TG_TOKEN = "6656018754:AAEiySDxp4qF-DxZqG-d-Mk2od0k4ljGGBY"

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'static_files', 'db.json')

VOSK_MODELS = {
    'ru': os.path.join(BASE_DIR, 'static_files', 'vosk-model-small-ru-0.22'),
    'en': os.path.join(BASE_DIR, 'static_files', 'vosk-model-en-us-0.22'),
    'cn': os.path.join(BASE_DIR, 'static_files', 'vosk-model-cn-0.22'),
}

MISTRAL_API_KEY = "JqBJDmM0zUFSXeq63JujtwhAlExw6nmV"
MISTRAL_API_URL = "https://api.mistral.ai/v1/models/mistral-7b-instruct/completions"
