from fastapi import FastAPI
from lamoda.routers import lamoda_router

app = FastAPI()
app.include_router(lamoda_router)


@app.get("/")
def main():
    return {"message": "success"}
