from datetime import datetime
from typing import Optional

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


class LamodaCategory(BaseModel):
    id: Optional[OID]
    category_title: str
    product_links: list[str]
    created_at: datetime = datetime.utcnow()
    url: str


class LamodaProduct(BaseModel):
    id: Optional[OID]
    product_sku: str
    product_type: str
    product_title: str
    brand: str
    created_at: datetime = datetime.utcnow()
    price: str
    attributes: list[dict]
    category_id: Optional[OID]
    url: str
