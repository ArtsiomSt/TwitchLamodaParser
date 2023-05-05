from pydantic import BaseModel


class TestModel(BaseModel):
    name: str
    description: str
    completed: bool
