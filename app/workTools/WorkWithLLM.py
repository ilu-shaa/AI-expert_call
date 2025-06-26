# app/workTools/WorkWithLLM.py

import httpx
from app.config import OPENROUTER_API_KEY

class MistralAPI:
    ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com",  # можно удалить или заменить
        "X-Title": "VTOL Assistant"
    }

    @staticmethod
    async def query(prompt: str, system: str = "You are a VTOL drone expert.", max_tokens: int = 256, temperature: float = 0.7) -> str:
        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(MistralAPI.ENDPOINT, headers=MistralAPI.HEADERS, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
