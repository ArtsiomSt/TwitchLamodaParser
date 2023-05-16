from fastapi import FastAPI

from config import Settings
from db import lamoda_db, twitch_db
from lamoda.routers import lamoda_router
from twitch.routers import twitch_router

app = FastAPI()
app.include_router(lamoda_router)
app.include_router(twitch_router)


@app.on_event("startup")
async def startup():
    settings = Settings()
    lamoda_db.connect_to_database(
        path=settings.mongo_url, db_name=settings.lamoda_db_name
    )
    twitch_db.connect_to_database(
        path=settings.mongo_url, db_name=settings.twitch_db_name
    )


@app.on_event("shutdown")
async def shutdown():
    lamoda_db.close_database_connection()
    twitch_db.close_database_connection()


@app.get("/")
def main():
    return {"message": "success"}
