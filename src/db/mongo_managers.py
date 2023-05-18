from typing import Any

from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from lamoda.schemas import LamodaCategory, LamodaProduct
from twitch.schemas import TwitchStream, TwitchUser

from .database_managers import LamodaDatabaseManager, TwitchDatabaseManager


class MongoLamodaManager(LamodaDatabaseManager):
    db: AsyncIOMotorDatabase = None
    client: AsyncIOMotorClient = None
    product_collection: AsyncIOMotorCollection = None
    category_collection: AsyncIOMotorCollection = None

    async def connect_to_database(self, path: str, db_name: str):
        self.client = AsyncIOMotorClient(path)
        self.db = self.client[db_name]
        self.product_collection = self.db.lamoda_p
        self.category_collection = self.db.lamoda_c

    async def close_database_connection(self):
        self.client.close()

    async def save_one_product(self, product: LamodaProduct) -> str:
        dict_from_product = product.dict()
        if await self.product_collection.find_one(
            {"url": product.url, "category_id": product.category_id}
        ):
            created_id = await self.product_collection.find_one_and_replace(
                {"url": product.url}, dict_from_product
            )
            product.id = str(created_id["_id"])
            return str(created_id["_id"])
        created_id = await self.product_collection.insert_one(dict_from_product)
        product.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    async def get_one_product(self, product_id: ObjectId) -> LamodaProduct:
        product = await self.product_collection.find_one({"_id": product_id})
        product["id"] = product["_id"]
        return LamodaProduct(**product)

    async def get_products_by_filter(self, query_filter: dict) -> list[LamodaProduct]:
        result_list = []
        async for product in self.product_collection.find(query_filter):
            product["id"] = product["_id"]
            result_list.append(LamodaProduct(**product))
        return result_list

    async def save_one_category(self, category: LamodaCategory) -> str:
        if await self.category_collection.find_one({"url": category.url}):
            created_id = await self.category_collection.find_one_and_replace(
                {"url": category.url}, category.dict()
            )
            category.id = created_id["_id"]
            return str(created_id["_id"])
        created_id = await self.category_collection.insert_one(category.dict())
        category.id = created_id.inserted_id
        return str(created_id.inserted_id)

    async def get_one_category(self, category_id: ObjectId) -> LamodaCategory:
        category = await self.category_collection.find_one({"_id": category_id})
        category["id"] = category["_id"]
        category["products"] = await self.get_products_by_filter(
            {"category_id": str(category["id"])}
        )
        return LamodaCategory(**category)

    async def get_categories_by_filter(
        self, query_filter: dict
    ) -> list[LamodaCategory]:
        result_list = []
        async for category in self.category_collection.find(query_filter):
            category["id"] = category["_id"]
            result_list.append(LamodaCategory(**category))
        return result_list

    async def get_test_message(self, message: str) -> Any:
        # method for my personal tests, would like to keep it for now
        return {"message": message}


class MongoTwitchManager(TwitchDatabaseManager):
    db: AsyncIOMotorDatabase = None
    client: AsyncIOMotorClient = None
    users_collection: AsyncIOMotorCollection = None
    streams_collection: AsyncIOMotorCollection = None
    games_collection: AsyncIOMotorCollection = None

    async def connect_to_database(self, path: str, db_name: str):
        self.client = AsyncIOMotorClient(path)
        self.db = self.client[db_name]
        self.users_collection = self.db.twitch_u
        self.streams_collection = self.db.twitch_s
        self.games_collection = self.db.twitch_g

    async def close_database_connection(self):
        self.client.close()

    async def save_one_user(self, user: TwitchUser) -> str:
        created_id = await self.users_collection.insert_one(user.dict())
        user.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    async def save_one_stream(self, stream: TwitchStream) -> str:
        user = stream.user
        await self.save_one_user(user)
        created_id = await self.streams_collection.insert_one(stream.dict())
        stream.id = str(created_id.inserted_id)
        return str(created_id.inserted_id)

    async def get_test_message(self, message: str) -> Any:
        # method for my personal tests, would like to keep it for now
        return {"message": message}
