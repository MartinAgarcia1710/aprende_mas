from pymongo import MongoClient

# Reemplazás con tus credenciales de MongoDB Atlas
MONGO_URI = "mongodb+srv://RugbyManager:RugbyManager@rugbymanager.krzyq6l.mongodb.net/?appName=RugbyManager"

def get_mongo_db():
    client = MongoClient(MONGO_URI)
    return client['aula_virtual']