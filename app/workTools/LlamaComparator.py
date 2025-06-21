from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from app.config import LLAMA2_PATH

class LlamaComparator:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(LLAMA2_PATH)
        self.model     = AutoModelForCausalLM.from_pretrained(
            LLAMA2_PATH,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.gen = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=False
        )

    def compare(self, name1: str, specs1: dict, name2: str, specs2: dict) -> str:
        prompt = f"""Сравните два VTOL‑дрона по ключевым параметрам:
Модель A: {name1}, характеристики: {specs1}
Модель B: {name2}, характеристики: {specs2}
Выделите, по каким параметрам какая модель лучше, и сделайте краткий вывод."""
        out = self.gen(prompt)[0]["generated_text"]
        # уберём повтор промпта
        return out.replace(prompt, "").strip()
