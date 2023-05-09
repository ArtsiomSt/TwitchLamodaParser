from pymongo import MongoClient
from pymongo.collection import Collection

client = MongoClient("mongodb://db:27017/")

db = client.todos_db

collection: Collection = db["todos"]
