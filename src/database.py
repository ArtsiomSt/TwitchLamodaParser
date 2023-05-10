from config import Settings
from pymongo import MongoClient
from pymongo.collection import Collection

settings = Settings()
client = MongoClient(settings.mongo_url)

db = client[settings.db_name]

lamoda_collection: Collection = db["lamoda"]


async def get_lamoda_collection() -> Collection:
    return lamoda_collection
