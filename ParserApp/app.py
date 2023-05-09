from fastapi import FastAPI

from routers.lamoda_parsers import lamoda_router
from routers.todos import todo_api_router

app = FastAPI()
app.include_router(todo_api_router, prefix="/todo")
app.include_router(lamoda_router, prefix="/lamoda")


@app.get("/")
def main():
    return {"message": "success"}
