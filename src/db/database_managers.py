from abc import abstractmethod
from typing import Protocol

from bson import ObjectId

from lamoda.schemas import LamodaProduct


class LamodaDatabaseManager(Protocol):
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
    def save_one_product(self, product: LamodaProduct) -> str:
        """Implementing of saving one LamodaProduct"""

    @abstractmethod
    def get_one_product(self, product_id: ObjectId) -> LamodaProduct:
        """Implementing of getting product by unique identifiers"""

    @abstractmethod
    def get_test_message(self, message: str) -> dict:
        """test"""
