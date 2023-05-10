from pydantic import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017/"
    db_name: str = "parser"

    class Config:
        fields = {
            "mongo_url": {
                "env": "DATABASE_URL",
            },
            "db_name": {
                "env": "LAMODA_DB_NAME",
            },
        }
