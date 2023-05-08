from fastapi import APIRouter
from settings.db import collection
from models.todos import Todo
from schemas.todos import todo_serializer, todos_serializer
from bson import ObjectId


todo_api_router = APIRouter()


@todo_api_router.get('/')
async def get_todos():
    todos = todos_serializer(collection.find())
    return {"data": todos}


@todo_api_router.get("/{idt}")
async def get_todo(idt: str):
    return todos_serializer(collection.find({"_id": ObjectId(idt)}))


@todo_api_router.post("/")
async def post_todo(todo: Todo):
    created_id = collection.insert_one(dict(todo))
    print(created_id)
    todo = todos_serializer(collection.find({"_id": created_id.inserted_id}))
    return todo
