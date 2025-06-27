#!/usr/bin/env python3
"""
compare.py

Скрипт для сравнения VTOL-дронов из локальной базы через модель deepseek-r1:8b.
"""

import os
import json
import argparse
import ollama

DB_PATH = os.path.join(os.path.dirname(__file__), 'app', 'static_files', 'db.json')
DEFAULT_MODEL = 'deepseek-r1:8b'

def load_db(path: str) -> dict:
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def build_prompt(chosen: list[tuple[str, dict]]) -> str:
    """
    Формируем строку вида:
    "Compare VTOL drones by key params: NameA: {...}; NameB: {...}; NameC: {...}"
    """
    parts = []
    for name, specs in chosen:
        # Спецификацию сериализуем компактно, чтобы deepseek видел все поля
        specs_json = json.dumps(specs, ensure_ascii=False)
        parts.append(f"{name}: {specs_json}")
    return "Сравните следующие VTOL-дроны по ключевым параметрам: " + "; ".join(parts)

def compare_models(models: list[str]):
    db = load_db(DB_PATH)

    # Проверка наличия
    missing = [m for m in models if m not in db]
    if missing:
        print(f"❌ В базе не найдены модели: {missing}")
        return

    # Собираем пары (имя, specs)
    chosen = [(m, db[m]) for m in models]

    prompt = build_prompt(chosen)

    try:
        resp = ollama.chat(
            model=DEFAULT_MODEL,
            messages=[
                {'role': 'system', 'content': 'Ты — эксперт по VTOL-дронам. Сравни модели по ключевым параметрам.'},
                {'role': 'user',   'content': prompt}
            ]
        )
        report = resp['message']['content']
        print("👉 Сравнение:\n")
        print(report)

    except Exception as e:
        print("❌ Ошибка при обращении к Ollama-серверу:")
        print(e)
        print("\nПроверьте, пожалуйста:")
        print("1) Что Ollama-сервис запущен и слушает на localhost:11434")
        print("2) Что модель deepseek-r1:8b установлена (ollama list)")
        print("3) При необходимости скорректируйте OLLAMA_BASE_URL")

def main():
    parser = argparse.ArgumentParser(
        description="Сравнить VTOL-дроны из локальной db.json через модель deepseek-r1:8b"
    )
    parser.add_argument(
        'models', nargs='+',
        help='Список названий моделей для сравнения (минимум 2)'
    )
    args = parser.parse_args()

    if len(args.models) < 2:
        parser.error("Нужно указать минимум две модели для сравнения.")

    compare_models(args.models)

if __name__ == "__main__":
    main()
