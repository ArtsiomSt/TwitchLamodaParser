from typing import Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from lamoda.schemas import LamodaCategory, LamodaProduct
from twitch.schemas import TwitchUser, TwitchStream

from .database_managers import LamodaDatabaseManager, TwitchDatabaseManager


class MongoLamodaManager(LamodaDatabaseManager):
    db: Database = None
    client: MongoClient = None
    product_collection: Collection = None
    category_collection: Collection = None

    def connect_to_database(self, path: str, db_name: str):
        self.client = MongoClient(path)
        self.db = self.client[db_name]
        self.product_collection = self.db.lamoda_p
        self.category_collection = self.db.lamoda_c

    def close_database_connection(self):
        self.client.close()

    def save_one_product(self, product: LamodaProduct) -> str:
        dict_from_product = product.dict()
        if self.product_collection.find_one(
            {"url": product.url, "category_id": product.category_id}
        ):
            created_id = self.product_collection.find_one_and_replace(
                {"url": product.url}, dict_from_product
            )
            product.id = str(created_id["_id"])
            return str(created_id["_id"])
        created_id = self.product_collection.insert_one(dict_from_product)
        product.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    def get_one_product(self, product_id: ObjectId) -> LamodaProduct:
        product = self.product_collection.find_one({"_id": product_id})
        product["id"] = product["_id"]
        return LamodaProduct(**product)

    def get_products_by_filter(self, query_filter: dict) -> list[LamodaProduct]:
        result_list = []
        for product in self.product_collection.find(query_filter):
            product["id"] = product["_id"]
            result_list.append(LamodaProduct(**product))
        return result_list

    def save_one_category(self, category: LamodaCategory) -> str:
        if self.category_collection.find_one({"url": category.url}):
            created_id = self.category_collection.find_one_and_replace(
                {"url": category.url}, category.dict()
            )
            category.id = created_id['_id']
            return str(created_id["_id"])
        created_id = self.category_collection.insert_one(category.dict())
        category.id = created_id.inserted_id
        return str(created_id.inserted_id)

    def get_one_category(self, category_id: ObjectId) -> LamodaCategory:
        category = self.category_collection.find_one({"_id": category_id})
        category["id"] = category["_id"]
        return LamodaCategory(**category)

    def get_categories_by_filter(self, query_filter: dict) -> list[LamodaCategory]:
        result_list = []
        for category in self.category_collection.find(query_filter):
            category["id"] = category["_id"]
            result_list.append(LamodaCategory(**category))
        return result_list

    def get_test_message(self, message: str) -> Any:
        # method for my personal tests, would like to keep it for now
        product = self.category_collection.find_one(
            {"url": "https://www.lamoda.by/c/5971/shoes-muzhkrossovki/"}
        )
        print(product)
        for item in self.product_collection.find({"category_id": str(product["_id"])}):
            print(item)
        return {"message": message}


class MongoTwitchManager(TwitchDatabaseManager):
    db: Database = None
    client: MongoClient = None
    users_collection: Collection = None
    streams_collection: Collection = None
    games_collection: Collection = None

    def connect_to_database(self, path: str, db_name: str):
        self.client = MongoClient(path)
        self.db = self.client[db_name]
        self.users_collection = self.db.twitch_u
        self.streams_collection = self.db.twitch_s
        self.games_collection = self.db.twitch_g

    def close_database_connection(self):
        self.client.close()

    def save_one_user(self, user: TwitchUser) -> str:
        created_id = self.users_collection.insert_one(user.dict())
        user.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    def save_one_stream(self, stream: TwitchStream) -> str:
        user = stream.user
        self.save_one_user(user)
        created_id = self.streams_collection.insert_one(stream.dict())
        stream.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    def get_test_message(self, message: str) -> Any:
        # method for my personal tests, would like to keep it for now
        #self.streams_collection.delete_many({})
        for item in self.streams_collection.find():
            print(item)
        print()
        # self.users_collection.delete_many({})
        for item in self.users_collection.find():
            print(item)
        return {"message": message}
