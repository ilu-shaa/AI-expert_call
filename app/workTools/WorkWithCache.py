import json
import os
import base64

class WorkWithCache:
    path = os.getcwd().replace("\\", "/") + "/app/static_files/tts_cache.json"
    @staticmethod
    def append_cache(key: str, cache_bytes: bytes, text : str):
        with open(WorkWithCache.path, 'r') as file:
            data = json.load(file)

        data[key] = [base64.b64encode(cache_bytes).decode('utf-8'), text]

        with open(WorkWithCache.path, 'w') as file:
            file.write(json.dumps(data))
    
    @staticmethod
    def check_key(key: str):
        with open(WorkWithCache.path, 'r') as file:
            data = json.load(file)

        if key in data.keys():
            return True
        else:
            return False
    
    @staticmethod
    def get_cache(key: str):
        with open(WorkWithCache.path, 'r') as file:
            data = json.load(file)

        return base64.b64decode(data[key][0]), data[key][1]