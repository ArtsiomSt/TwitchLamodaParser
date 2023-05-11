from .database_managers import LamodaDatabaseManager
from .mongo_managers import MongoLamodaManager

lamoda_db = MongoLamodaManager()


def get_lamoda_database() -> LamodaDatabaseManager:
    return lamoda_db
