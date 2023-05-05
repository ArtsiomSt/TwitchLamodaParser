from pymongo import MongoClient

client = MongoClient('mongodb://db:27017/')

db = client.test_db

collection = db['test_app']
