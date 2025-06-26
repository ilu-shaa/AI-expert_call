# app/workTools/DeepseekComparator.py

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

class DeepseekComparator:
    def __init__(self):
        model_name = "deepseek-r1:8b"
        # Загружаем токенизатор и модель
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        # Создаём пайплайн для генерации
        self.gen = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,
            temperature=0.2,  # чуть более высокая температура для вариативности
            do_sample=True,   # включаем сэмплинг
            top_p=0.9,        # nucleus sampling
        )

    def compare(self, name_a: str, specs_a: dict, name_b: str, specs_b: dict, locale: str = "ru") -> str:
        """
        Сравнивает два продукта по ключевым параметрам.
        name_a, specs_a — название и dict характеристик первого дрона.
        name_b, specs_b — название и dict характеристик второго дрона.
        locale — 'ru' или 'en', влияет на язык ответа.
        """
        # Преобразуем dict в краткую строку для промпта
        def specs_to_str(name: str, specs: dict) -> str:
            parts = []
            for key, value in specs.items():
                parts.append(f"{key}: {value}")
            return f"{name} ({'; '.join(parts)})"

        a_str = specs_to_str(name_a, specs_a)
        b_str = specs_to_str(name_b, specs_b)

        # Формируем итоговый промпт
        if locale == "en":
            prompt = (
                "Compare the following two VTOL drones by key parameters:\n"
                f"- Model A: {a_str}\n"
                f"- Model B: {b_str}\n"
                "Highlight for which parameters each model is better and give a brief conclusion."
            )
        else:
            prompt = (
                "Сравните два VTOL-дрона по ключевым параметрам:\n"
                f"Модель A: {a_str}\n"
                f"Модель B: {b_str}\n"
                "Выделите, по каким параметрам какая модель лучше, и сделайте краткий вывод."
            )

        # Генерируем ответ
        output = self.gen(prompt)[0]["generated_text"]

        # Убираем эхо промпта, если модель его повторила
        return output.replace(prompt, "").strip()
