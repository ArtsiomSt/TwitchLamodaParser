import json
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends

from brokers.producer import producer
from cache import RedisCacheManager
from core.enums import ObjectStatus
from db import get_lamoda_database
from db.database_managers import LamodaDatabaseManager
from dependecies import get_cache_manager
from lamoda.config import LamodaSettings
from lamoda.service import (
    parse_lamoda_category,
    parse_links_from_category,
    parse_object,
)
from lamoda.schemas import CategoryUrl, ProductUrl
from schemas import LamodaResponseFromParser

lamoda_router = APIRouter(prefix="/lamoda")

LamodaDb = Annotated[LamodaDatabaseManager, Depends(get_lamoda_database)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]
settings = LamodaSettings()


@lamoda_router.post("/parse/product")
async def parse_product(url: ProductUrl, db: LamodaDb, cache: CacheMngr):
    """
    View for parsing product by its url, processed product is saved to cache and db
    It should not be called directly, because of it has to calculate a lot of info,
    Should be called from kafka.
    """

    params = {}
    key_for_cache = {"url": url.url, "params": params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache and object_from_cache["status"] == ObjectStatus.PROCESSED.name:
        return {"message": "object is already processed"}
    product = parse_object(url.url)
    await db.save_one_product(product)
    await cache.save_to_cache(
        key_for_cache,
        60 * 5,
        LamodaResponseFromParser(
            url=url.url, status=ObjectStatus.PROCESSED.name, params=params, data=product
        ),
    )
    return {"message": "processed"}


@lamoda_router.post("/parse/category")
async def parse_category(url: CategoryUrl, db: LamodaDb, cache: CacheMngr):
    """
    View for parsing category, processed category is saved to cache and db
    It should not be called directly, because of it has to calculate a lot of info,
    Should be called from kafka.
    """

    params = {}
    key_for_cache = {"url": url.url, "params": params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache and object_from_cache["status"] == ObjectStatus.PROCESSED.name:
        return {"message": "object is already processed"}
    category = parse_lamoda_category(url.url)
    category_id = await db.save_one_category(category)
    created_category = await db.get_one_category(ObjectId(category_id))
    for product in parse_links_from_category(created_category):
        await db.save_one_product(product)
    created_category = await db.get_one_category(ObjectId(category_id))
    await cache.save_to_cache(
        key_for_cache,
        60 * 5,
        LamodaResponseFromParser(
            url=url.url,
            status=ObjectStatus.PROCESSED.name,
            params=params,
            data=created_category,
        ),
    )
    return {"message": "processed"}


@lamoda_router.post("/product", response_model=LamodaResponseFromParser)
async def get_parsed_products(url: ProductUrl, cache: CacheMngr):
    """
    This view stands for sending requests for parsing products
    using kafka, products are parsed in other application. Kafka then sends request to
    /parse/product of another similar application, that processes request
    """

    params = {}
    key_for_cache = {"url": url.url, "params": params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    await cache.save_to_cache(
        key_for_cache,
        60 * 5,
        LamodaResponseFromParser(
            url=url.url, status=ObjectStatus.PENDING.name, params=params
        ),
    )
    producer.produce(
        settings.lamoda_products_topic,
        key="parse_product",
        value=json.dumps(key_for_cache),
    )
    return LamodaResponseFromParser.parse_obj(
        {"url": url.url, "params": params, "status": ObjectStatus.CREATED.name}
    )


@lamoda_router.post("/category", response_model=LamodaResponseFromParser)
async def get_parsed_categories(url: CategoryUrl, cache: CacheMngr):
    """
    This view stands for sending requests for parsing categories
    using kafka, products are parsed in other application. Kafka then sends request to
    /parse/category of another similar application, that processes request.
    """

    params = {}
    key_for_cache = {"url": url.url, "params": params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    await cache.save_to_cache(
        key_for_cache,
        60 * 3,
        LamodaResponseFromParser(
            url=url.url, status=ObjectStatus.PENDING.name, params=params
        ),
    )
    producer.produce(
        settings.lamoda_category_topic,
        key="parse_category",
        value=json.dumps(key_for_cache),
    )
    return LamodaResponseFromParser.parse_obj(
        {"url": url.url, "params": params, "status": ObjectStatus.CREATED.name}
    )


@lamoda_router.get("/test")
async def test_message(db: LamodaDb):
    await db.get_test_message("works")
