from typing import Any

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from lamoda.schemas import LamodaProduct, LamodaCategory

from .database_managers import LamodaDatabaseManager


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
        if self.product_collection.find_one({"url": product.url}):
            created_id = self.product_collection.find_one_and_replace(
                {"url": product.url}, dict_from_product
            )
            return str(created_id["_id"])
        created_id = self.product_collection.insert_one(dict_from_product)
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
            return str(created_id["_id"])
        created_id = self.category_collection.insert_one(category.dict())
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

    def get_test_message(
        self, message: str
    ) -> Any:  # method for my personal tests, would like to keep it for now)
        return {"message": message}
