from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017/"
    lamoda_db_name: str = "parser_lamoda"
    twitch_db_name: str = "parser_twitch"

    class Config:
        fields = {
            "mongo_url": {
                "env": "DATABASE_URL",
            },
            "lamoda_db_name": {
                "env": "LAMODA_DB_NAME",
            },
            "twitch_db_name": {
                "env": "TWITCH_DB_NAME"
            }
        }
