import json
import os

class WorkWithDB:
    @staticmethod
    def show_characteristics(model_name: str) -> dict:
        db_path = os.path.join("static_files", "drones.json")
        if not os.path.exists(db_path):
            return {}
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(model_name, {})
