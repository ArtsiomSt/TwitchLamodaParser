from decimal import Decimal

from bson import Decimal128, ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from lamoda.schemas import LamodaProduct

from .database_managers import LamodaDatabaseManager


class MongoLamodaManager(LamodaDatabaseManager):
    db: Database = None
    client: MongoClient = None
    collection: Collection = None

    def connect_to_database(self, path: str, db_name: str):
        self.client = MongoClient(path)
        self.db = self.client[db_name]
        self.collection = self.db.lamoda

    def close_database_connection(self):
        self.client.close()

    def save_one_product(self, product: LamodaProduct) -> str:
        dict_from_product = product.dict()
        for key, value in dict_from_product.items():
            if isinstance(value, Decimal):
                dict_from_product[key] = Decimal128(value)
        created_id = self.collection.insert_one(dict_from_product)
        return str(created_id.inserted_id)

    def get_one_product(self, product_id: ObjectId) -> LamodaProduct:
        product = self.collection.find_one({"_id": product_id})
        product["id"] = product["_id"]
        return LamodaProduct(**product)

    def get_test_message(self, message: str) -> dict:
        return {"message": message}
