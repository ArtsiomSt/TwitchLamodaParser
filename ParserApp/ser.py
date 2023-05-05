def serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "name": todo['name'],
        "description": todo['description'],
    }


def many_serializer(todos) -> list:
    return [serializer(todo) for todo in todos]