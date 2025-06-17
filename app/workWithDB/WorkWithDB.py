import json

class WorkWithDb:
    path = "C:/Users/Proger/Documents/AI-expert_call/app/workWithDB/db.json" # путь до db.json
    @staticmethod
    def show_characteristics(drone_name: str) -> dict:
        with open(WorkWithDb.path, 'r') as file:
            data = json.load(file)
        
        return data[drone_name] # возвращает json с характеристиками