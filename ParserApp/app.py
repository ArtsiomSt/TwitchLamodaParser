from fastapi import FastAPI
from routers.todos import todo_api_router
from parsers.lamoda_parsers import parse_object


app = FastAPI()
app.include_router(todo_api_router, prefix="/todo")


@app.get("/")
def main():
    parse_object()
    return {"message": "success"}


