import httpx
from app.config import OPENROUTER_API_KEY

class MistralAPI:
    ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }

    @staticmethod
    async def query(prompt: str, system: str = "You are a VTOL–drone expert.") -> str:
        async with httpx.AsyncClient(timeout=15) as cli:
            payload = {
                "model": "mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 512
            }
            r = await cli.post(MistralAPI.ENDPOINT, json=payload, headers=MistralAPI.HEADERS)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
