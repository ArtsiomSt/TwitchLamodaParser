from fastapi import FastAPI

from routers.lamoda_routers import lamoda_router

app = FastAPI()
app.include_router(lamoda_router, prefix="/lamoda")


@app.get("/")
def main():
    return {"message": "success"}
