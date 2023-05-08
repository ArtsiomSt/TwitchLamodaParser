import os

from pymongo.collection import Collection
from pymongo import MongoClient

client = MongoClient('mongodb://db:27017/')

db = client.todos_db

collection: Collection = db['todos']
