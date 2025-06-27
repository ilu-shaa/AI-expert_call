#!/usr/bin/env python3
"""
test.py

Простой скрипт для теста связи с локальным Ollama-сервером
и моделью deepseek-r1:8b без использования несуществующего класса Ollama.
"""

import os
import ollama

def main():
    # Если ваш Ollama-сервис слушает на нестандартном порту/хосте,
    # укажите это здесь (иначе строку можно закомментировать):
    # os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:11435"

    user_prompt = "Напиши функцию на Python, которая считает факториал."

    try:
        # Делаем запрос напрямую
        response = ollama.chat(
            model='deepseek-r1:8b',       # имя вашей модели
            messages=[
                {'role': 'system', 'content': 'Ты — ассистент-программист.'},
                {'role': 'user', 'content': user_prompt}
            ]
        )

        ai_message = response['message']['content']
        print("Запрос:\n", user_prompt)
        print("\nОтвет модели:\n", ai_message)

    except Exception as e:
        print("❌ Ошибка при обращении к Ollama-серверу:")
        print(e)
        print("\nПроверьте, пожалуйста:")
        print("1) Что Ollama-сервис запущен и слушает на localhost:11434")
        print("2) Что модель deepseek-r1:8b есть в списке `ollama list`")
        print("3) При необходимости скорректируйте OLLAMA_BASE_URL")

if __name__ == "__main__":
    main()
