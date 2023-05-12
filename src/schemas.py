from typing import Optional
from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v == "":
            raise TypeError("ObjectId is empty")
        if not ObjectId.is_valid(v):
            raise TypeError("ObjectId invalid")
        return str(v)


class CustomModel(BaseModel):
    id: Optional[OID]
    created_at: datetime = datetime.utcnow()
