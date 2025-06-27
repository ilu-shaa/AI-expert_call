import json
import os
from app.config import DB_PATH
class WorkWithDB:
    @staticmethod
    def show_characteristics(model_name: str) -> dict:
        if not os.path.exists(DB_PATH):
            return {}
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(model_name, {})

    @staticmethod
    def load_all() -> dict:
        """
        Загружает всю базу данных дронов.
        """
        if not os.path.exists(DB_PATH):
            return {}
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
