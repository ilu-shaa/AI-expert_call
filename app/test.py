import json

# Загрузка данных из файла
with open('C:/Users/Proger/Documents/AI-expert_call/app/static_files/tts_cache.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Удаление ключа, если он существует
key_to_remove = "presentaion_JOUAV CW-15en"
if key_to_remove in data:
    data.pop(key_to_remove)

# Сохранение обновлённых данных обратно в файл
with open('C:/Users/Proger/Documents/AI-expert_call/app/static_files/tts_cache.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)