import json
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends

from brokers.producer import producer
from cache import RedisCacheManager
from db import get_lamoda_database
from db.database_managers import LamodaDatabaseManager
from dependecies import get_cache_manager
from lamoda.config import LamodaSettings
from lamoda.service import (
    parse_lamoda_category,
    parse_links_from_category,
    parse_object,
)
from schemas import LamodaResponseFromParser

lamoda_router = APIRouter(prefix="/lamoda")

LamodaDb = Annotated[LamodaDatabaseManager, Depends(get_lamoda_database)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]
settings = LamodaSettings()


@lamoda_router.post("/product")
def parse_product(url: str, db: LamodaDb, cache: CacheMngr):
    """View for parsing product by its url, processed product is saved to cache and db"""

    params = {}
    key_for_cache = {"url": url, "params": params}
    object_from_cache = cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        if object_from_cache["status"] == "processed":
            return {"message": "object is already processed"}
    product = parse_object(url)
    db.save_one_product(product)
    cache.save_to_cache(
        key_for_cache,
        60 * 5,
        LamodaResponseFromParser(
            url=url, status="processed", params=params, data=product
        ),
    )
    return {"message": "processed"}


@lamoda_router.post("/category")
def parse_category(url: str, db: LamodaDb, cache: CacheMngr):
    """View for parsing category, processed category is saved to cache and db"""

    params = {}
    key_for_cache = {"url": url, "params": params}
    object_from_cache = cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        if object_from_cache["status"] == "processed":
            return {"message": "object is already processed"}
    category = parse_lamoda_category(url)
    category_id = db.save_one_category(category)
    created_category = db.get_one_category(ObjectId(category_id))
    for product in parse_links_from_category(created_category):
        db.save_one_product(product)
    created_category = db.get_one_category(ObjectId(category_id))
    cache.save_to_cache(
        key_for_cache,
        60 * 5,
        LamodaResponseFromParser(
            url=url, status="processed", params=params, data=created_category
        ),
    )
    return {"message": "processed"}


@lamoda_router.get("/parse/product", response_model=LamodaResponseFromParser)
def get_parsed_products(url: str, cache: CacheMngr):
    """
    This view stands for sending requests for parsing products
    using kafka, products are parsed in other application
    """

    params = {}
    key_for_cache = {"url": url, "params": params}
    object_from_cache = cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    cache.save_to_cache(
        key_for_cache,
        60 * 5,
        LamodaResponseFromParser(url=url, status="pending", params=params),
    )
    producer.produce(
        settings.lamoda_products_topic,
        key="parse_product",
        value=json.dumps(key_for_cache),
    )
    return LamodaResponseFromParser.parse_obj(
        {"url": url, "params": params, "status": "created"}
    )


@lamoda_router.get("/parse/category", response_model=LamodaResponseFromParser)
def get_parsed_categories(url: str, cache: CacheMngr):
    """
    This view stands for sending requests for parsing categories
    using kafka, categories are parsed in other application
    """

    params = {}
    key_for_cache = {"url": url, "params": params}
    object_from_cache = cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    cache.save_to_cache(
        key_for_cache,
        60 * 3,
        LamodaResponseFromParser(url=url, status="pending", params=params),
    )
    producer.produce(
        settings.lamoda_category_topic,
        key="parse_category",
        value=json.dumps(key_for_cache),
    )
    return LamodaResponseFromParser.parse_obj(
        {"url": url, "params": params, "status": "created"}
    )


@lamoda_router.get("/test")
def test_message(db: LamodaDb):
    return db.get_test_message("works")
