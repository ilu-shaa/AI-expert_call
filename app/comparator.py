#C:\Users\ilua-pc\Desktop\Export\AI-expert_call\app\comparator.py
import json
from typing import Dict, List, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import ollama

# Параметры, по которым сравниваем
KEY_PARAMS = [
    ("max_speed_kmh",    {"ru": "Макс. скорость (км/ч)", "en": "Max Speed (km/h)",    "cn": "最大速度 (公里/小时)"}),
    ("flight_time_min",  {"ru": "Время полёта (мин)",    "en": "Flight Time (min)",    "cn": "飞行时间 (分钟)"}),
    ("max_payload_kg",   {"ru": "Полезная нагрузка (кг)", "en": "Max Payload (kg)",     "cn": "有效载荷 (公斤)"}),
    ("max_range_km",     {"ru": "Дальность (км)",        "en": "Max Range (km)",       "cn": "最大航程 (公里)"}),
]

# Тексты для «ничья»
TIE_LABEL = {"ru": "Ничья", "en": "Tie", "cn": "平局"}


def load_db(path: str = "app/static_files/db.json") -> Dict[str, Dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _get_value(specs: Dict, key: str) -> Optional[float]:
    perf = specs.get("performance", {})
    w = specs.get("weights", {})
    val = perf.get(key)
    if val is None:
        val = w.get(key)
    return val


def compare_two_models(
    name_a: str, specs_a: Dict,
    name_b: str, specs_b: Dict,
    lang: str = "ru"
) -> List[str]:
    lines: List[str] = []
    for key, labels in KEY_PARAMS:
        a_val = _get_value(specs_a, key)
        b_val = _get_value(specs_b, key)
        if a_val is None or b_val is None:
            continue

        if a_val > b_val:
            winner = name_a
        elif b_val > a_val:
            winner = name_b
        else:
            winner = TIE_LABEL[lang]

        label = labels[lang]
        lines.append(f"{label}: {a_val} vs {b_val} → {winner}")
    return lines


def compare_main_vs(
    main: str,
    competitors: List[str],
    lang: str = "ru"
) -> str:
    """
    Сравнивает одну модель main с листом competitors, используя DeepSeek через Ollama.
    """
    db = load_db()
    specs_main = db.get(main)
    if not specs_main:
        return {"ru":"Модель не найдена в базе.","en":"Model not found.","cn":"未找到该型号。"}[lang]

    report_lines: List[str] = []
    report_lines.append({
        'ru': f"📊 Сравнение «{main}» с конкурентами:",
        'en': f"📊 Comparison of {main} vs competitors:",
        'cn': f"📊 {main} 与竞品比较："
    }[lang])
    report_lines.append("")

    for comp in competitors:
        specs_comp = db.get(comp)
        if not specs_comp:
            report_lines.append({
                'ru': f"Конкурент {comp} не найден.",
                'en': f"Competitor {comp} not found.",
                'cn': f"未找到竞品 {comp}。"
            }[lang])
            continue
        # Структурированное сравнение
        report_lines.append({
            'ru': f"— {main} vs {comp}:", 'en': f"— {main} vs {comp}:", 'cn': f"— {main} vs {comp}："
        }[lang])
        report_lines.extend(compare_two_models(main, specs_main, comp, specs_comp, lang))
        report_lines.append("")

        # Подготовка prompt для DeepSeek
        summary_prompt = f"Compare these two VTOL drones: {main} and {comp}. Specs of {main}: {json.dumps(specs_main)}. Specs of {comp}: {json.dumps(specs_comp)}. Summarize the key differences and which is better overall."

        try:
            deepseek_response = ollama.chat(
                model='deepseek-r1:8b',
                messages=[{'role': 'user', 'content': summary_prompt}]
            )
            deepseek_text = deepseek_response['message']['content']
        except Exception as e:
            deepseek_text = f"[DeepSeek error: {e}]"

        report_lines.append({
            'ru': '🤖 Анализ ИИ:', 'en': '🤖 AI analysis:', 'cn': '🤖 AI分析：'
        }[lang])
        report_lines.append(deepseek_text)
        report_lines.append("")

    return "\n".join(report_lines)


def list_by_country(
    country: str,
    lang: str = "ru"
) -> str:
    db = load_db()
    filtered = [name for name, spec in db.items() if spec.get("country","...").lower() == country.lower()]
    if not filtered:
        return {"ru": f"Модели из {country} не найдены.", "en": f"No models from {country}.", "cn": f"未找到来自{country}的型号。"}[lang]
    header = {"ru": f"Дроны из {country}:", "en": f"Drones from {country}:", "cn": f"来自{country}的无人机："}[lang]
    return "\n".join([header] + [f"• {n}" for n in filtered])
