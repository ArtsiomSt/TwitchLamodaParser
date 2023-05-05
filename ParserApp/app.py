from fastapi import FastAPI
from routers.model_router import todo_api_router

app = FastAPI()
app.include_router(todo_api_router, prefix="/todo")


@app.get("/")
def main():
    return {"message": "success"}
