from abc import abstractmethod
from typing import Any, Protocol

from bson import ObjectId

from lamoda.schemas import LamodaCategory, LamodaProduct
from twitch.schemas import TwitchUser, TwitchStream


class DatabaseManager(Protocol):
    @property
    def client(self):
        raise NotImplementedError

    @property
    def db(self):
        raise NotImplementedError

    @abstractmethod
    def connect_to_database(self, path: str, db_name: str):
        """Implementing db connect"""

    @abstractmethod
    def close_database_connection(self):
        """Implementing closing db connection"""

    @abstractmethod
    def get_test_message(self, message: str) -> Any:
        """This function is made for personal purposes and tests"""


class LamodaDatabaseManager(DatabaseManager):
    @abstractmethod
    def save_one_product(self, product: LamodaProduct) -> str:
        """Implementation of saving one LamodaProduct"""

    @abstractmethod
    def get_one_product(self, product_id: ObjectId) -> LamodaProduct:
        """Implementation of getting product by unique identifiers"""

    @abstractmethod
    def get_products_by_filter(self, query_filter: dict) -> list[LamodaProduct]:
        """Implementation of getting products by custom filter"""

    @abstractmethod
    def save_one_category(self, category: LamodaCategory) -> str:
        """Implementation of saving LamodaCategory"""

    @abstractmethod
    def get_one_category(self, product_id: ObjectId) -> LamodaCategory:
        """Implementation of getting product by unique identifiers"""

    @abstractmethod
    def get_categories_by_filter(self, query_filter: dict) -> list[LamodaCategory]:
        """Implementation of getting products by custom filter"""


class TwitchDatabaseManager(DatabaseManager):
    @abstractmethod
    def save_one_user(self, user: TwitchUser) -> str:
        """Implementing saving of user"""
