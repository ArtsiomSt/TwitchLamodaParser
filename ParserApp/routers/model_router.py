from fastapi import APIRouter
from settings.db import collection
from ser import many_serializer

todo_api_router = APIRouter()


@todo_api_router.get('/')
async def get_todos():
    todos = many_serializer(collection.find())
    return {"status": 200, "data": todos}
