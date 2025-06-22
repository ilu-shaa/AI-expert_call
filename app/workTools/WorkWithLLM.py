import httpx
import json
# from app.config import OPENROUTER_API_KEY

class MistralAPI:
    @staticmethod
    async def query(token, prompt: str, system: str = "You are a VTOL‑drone expert.") -> str: # добавил токен
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://yourdomain.com",  # Укажи свой домен
            "X-Title": "VTOL Drone Expert Bot"
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 512
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"].strip()