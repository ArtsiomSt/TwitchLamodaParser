from .database_managers import LamodaDatabaseManager, TwitchDatabaseManager
from .mongo_managers import MongoLamodaManager, MongoTwitchManager

lamoda_db = MongoLamodaManager()

twitch_db = MongoTwitchManager()


def get_lamoda_database() -> LamodaDatabaseManager:
    return lamoda_db


def get_twitch_database() -> TwitchDatabaseManager:
    return twitch_db
