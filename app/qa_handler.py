#ЕЩЕ В ПРОЦЕССЕЕ
import httpx
from app.config import MISTRAL_API_URL, MISTRAL_API_KEY
import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

qa_router = Router()

# 1. Шаблоны 15 типовых вопросов
TYPICAL_QUESTIONS = [
    "Каково максимальное время автономного полёта?",
    "Какую максимальную полезную нагрузку можно установить?",
    "Каков рабочий радиус (дальность) полёта?",
    "Какова максимальная и крейсерская скорость?",
    "Какие источники энергии и батареи используются?",
    "При каких температурах и условиях допускается эксплуатация?",
    "Какие каналы связи применяются для управления и телеметрии?",
    "Есть ли автопилот и системы обхода препятствий?",
    "Какие виды полезной нагрузки поддерживаются?",
    "Как выполняется запуск и посадка?",
    "Какие сертификаты и стандарты соответствия пройдены?",
    "Какова примерная стоимость и условия логистики?",
    "Какие схемы обслуживания предусмотрены?",
    "Как быстро готовится к вылету?",
    "Какова гарантия и ресурс аккумуляторов/моторов?"
]

# 2. Кнопочная клавиатура с вопросами
def build_qa_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    for idx, q in enumerate(TYPICAL_QUESTIONS, 1):
        kb.add(InlineKeyboardButton(f"{idx}. {q}", callback_data=f"qa:{idx-1}"))
    return kb

# 3. Команда для вывода списка вопросов
@qa_router.message(Command("questions"))
async def send_questions(msg):
    kb = build_qa_kb()
    await msg.answer("Выберите интересующий вопрос:", reply_markup=kb)

# 4. Обработчик выбора вопроса
@qa_router.callback_query(F.data.startswith("qa:"))
async def handle_qa(c: CallbackQuery):
    idx = int(c.data.split(":", 1)[1])
    question = TYPICAL_QUESTIONS[idx]
    await c.answer()  
    await c.message.edit_reply_markup()  

    prompt = (
        f"Вы — эксперт по VTOL‑дронам для китайского рынка.\n"
        f"У пользователя вопрос: «{question}»\n"
        f"Дайте подробный, но понятный ответ, "
        f"опираясь на данные из базы знаний."
    )
    answer = await ask_llm(prompt)
    await c.message.answer(f"❓ {question}\n\n💬 {answer}")

# 5. Функция-заглушка для вызова LLM через HTTP API
async def ask_llm(prompt: str) -> str:
    """
    Отправляет prompt запросом к Mistral Inference API v1 и возвращает текст ответа.
    """
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "max_new_tokens": 200,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    choices = data.get("choices", [])
    if not choices:
        return "Извините, не смог получить ответ от модели."
    return choices[0].get("text", "").strip()


