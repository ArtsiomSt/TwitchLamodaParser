from pymongo import MongoClient
from pymongo.collection import Collection

from config import Settings

settings = Settings()
client = MongoClient(settings.mongo_url)

db = client[settings.db_name]

lamoda_collection: Collection = db["lamoda"]
