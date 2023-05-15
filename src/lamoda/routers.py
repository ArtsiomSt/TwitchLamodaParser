from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends

from brokers.producer import producer
from db import get_lamoda_database
from db.database_managers import LamodaDatabaseManager
from dependecies import get_cache_manager
from cache import RedisCacheManager
from lamoda.schemas import LamodaProduct
from lamoda.service import (
    parse_lamoda_category,
    parse_links_from_category,
    parse_object,
)

lamoda_router = APIRouter(prefix="/lamoda")

LamodaDb = Annotated[LamodaDatabaseManager, Depends(get_lamoda_database)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]


@lamoda_router.post("/product", response_model=LamodaProduct)
def parse_product(url: str, db: LamodaDb, cache: CacheMngr):
    """View for parsing product by its url"""

    key_for_cache = {"url": url, "params": {}}
    object_from_cache = cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    product = parse_object(url)
    created_id = db.save_one_product(product)
    producer.produce("product", key="message", value="new_from_products")
    cache.save_to_cache(key_for_cache, 60*5, product)
    saved_product = db.get_one_product(ObjectId(created_id))
    return saved_product


@lamoda_router.post("/category")
def parse_category(url: str, db: LamodaDb, cache: CacheMngr):
    """View for parsing category"""

    key_for_cache = {"url": url, "params": {}}
    object_from_cache = cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    category = parse_lamoda_category(url)
    category_id = db.save_one_category(category)
    created_category = db.get_one_category(ObjectId(category_id))
    for product in parse_links_from_category(created_category):
        db.save_one_product(product)
    created_category = db.get_one_category(ObjectId(category_id))
    cache.save_to_cache(key_for_cache, 5*60, created_category)
    return {"message": "success"}


@lamoda_router.get("/test")
def test_message(db: LamodaDb):
    return db.get_test_message("works")
