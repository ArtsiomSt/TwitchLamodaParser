from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends

from db import get_lamoda_database
from db.database_managers import LamodaDatabaseManager
from lamoda.schemas import LamodaProduct
from lamoda.service import parse_object

lamoda_router = APIRouter(prefix="/lamoda")

LamodaDb = Annotated[LamodaDatabaseManager, Depends(get_lamoda_database)]


@lamoda_router.post("/product", response_model=LamodaProduct)
def parse_product(url: str, db: LamodaDb):
    """View for parsing product by its url"""

    product = parse_object(url)
    created_id = db.save_one_product(product)
    saved_product = db.get_one_product(ObjectId(created_id))
    return saved_product


@lamoda_router.get("/test")
def test_message(db: LamodaDb):
    print(db.client)
    print(db.db)
    return db.get_test_message("works")


@lamoda_router.get("/")
def main_page():
    return {"message": "success"}
