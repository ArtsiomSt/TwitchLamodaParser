from decimal import Decimal
from typing import Annotated

from bson import Decimal128
from database import Collection, get_lamoda_collection
from fastapi import APIRouter, Depends

from .utils import parse_object

lamoda_router = APIRouter(prefix='/lamoda')

LamodaCollection = Annotated[Collection, Depends(get_lamoda_collection)]


@lamoda_router.post("/product")
def parse_product(url: str, collection: LamodaCollection):
    """View for parsing product by its url"""

    product = parse_object(url)
    Decimal128(str(product.price))
    product_as_dict = product.dict()
    for key, value in product_as_dict.items():
        if isinstance(value, Decimal):
            product_as_dict[key] = str(value)
    product.price = str(product.price)
    created_id = collection.insert_one(product_as_dict)  # it is temporary, made to check the ability to save into db
    created = collection.find_one({"_id": created_id.inserted_id})  # soon will make other alg to save into db
    return product.dict()


@lamoda_router.get("/")
def main_page():
    return {"message": "success"}
