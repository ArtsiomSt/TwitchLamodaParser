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
from lamoda.schemas import (
    CategoryParams,
    ProductParams,
    ProductDbParams,
    CategoryDbParams,
    LamodaResponseFromParser,
)
from lamoda.service import (
    parse_lamoda_category,
    parse_links_from_category,
    parse_object,
)
from schemas import ResponseFromDb
from utils import get_available_params

lamoda_router = APIRouter(prefix="/lamoda")

LamodaDb = Annotated[LamodaDatabaseManager, Depends(get_lamoda_database)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]
settings = LamodaSettings()


@lamoda_router.post("/product/parse")
async def parse_product(url: ProductParams, db: LamodaDb, cache: CacheMngr):
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


@lamoda_router.post("/category/parse")
async def parse_category(url: CategoryParams, db: LamodaDb, cache: CacheMngr):
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
async def get_parsed_products(url: ProductParams, cache: CacheMngr):
    """
    This view stands for sending requests for parsing products
    using kafka, products are parsed in other application. Kafka then sends request to
    /parse/product of another similar application, that processes request
    """

    params = {}
    key_for_cache = {"url": url.url, "params": params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        object_from_cache.update({"paginate_by": 1, "page_num": 0})
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
        {
            "url": url.url,
            "params": params,
            "status": ObjectStatus.CREATED.name,
            "paginate_by": 1,
            "page_num": 0,
        }
    )


@lamoda_router.post("/category", response_model=LamodaResponseFromParser)
async def get_parsed_categories(url: CategoryParams, cache: CacheMngr):
    """
    This view stands for sending requests for parsing categories
    using kafka, products are parsed in other application. Kafka then sends request to
    /parse/category of another similar application, that processes request.
    """

    params = {}
    key_for_cache = {"url": url.url, "params": params}
    pagination = {"paginate_by": url.paginate_by, "page_num": url.page_num}
    object_from_cache = await cache.get_object_from_cache(
        key_for_cache, ["data", "products"], url.paginate_by, url.page_num
    )
    if object_from_cache:
        object_from_cache.update(pagination)
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
    return LamodaResponseFromParser(
        url=url.url, params=params, status=ObjectStatus.CREATED.name, **pagination
    )


@lamoda_router.get("/product")
async def get_products(
    db: LamodaDb, params: ProductDbParams = Depends()
) -> ResponseFromDb:
    """View that stands for getting products from database"""

    available_filters = ["product_type", "url"]
    filter_params = get_available_params(params.dict(), available_filters)
    products = await db.get_products_by_filter(
        filter_params, paginate_by=params.paginate_by, page_num=params.page_num
    )
    response_dict = {
        "status": ObjectStatus.PROCESSED.name,
        "data": products,
        "paginate_by": params.paginate_by,
        "page_num": params.page_num,
    }
    return ResponseFromDb(**response_dict)


@lamoda_router.get("/category")
async def get_categories(
    db: LamodaDb, params: CategoryDbParams = Depends()
) -> ResponseFromDb:
    """View that stands for getting some categories from database"""

    available_filters = ["url"]
    filter_params = get_available_params(params.dict(), available_filters)
    products = await db.get_categories_by_filter(
        filter_params,
        paginate_by=params.paginate_by,
        page_num=params.page_num,
        with_products=params.with_products,
    )
    response_dict = {
        "status": ObjectStatus.PROCESSED.name,
        "data": products,
        "paginate_by": params.paginate_by,
        "page_num": params.page_num,
    }
    return ResponseFromDb(**response_dict)


@lamoda_router.get("/test")
async def test_message(db: LamodaDb):
    await db.get_test_message("works")
