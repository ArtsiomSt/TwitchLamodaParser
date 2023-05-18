import json
from typing import Annotated

from fastapi import APIRouter, Depends

from brokers.producer import producer
from cache import RedisCacheManager
from core.enums import ObjectStatus
from db import get_twitch_database
from db.database_managers import TwitchDatabaseManager
from dependecies import get_cache_manager
from schemas import TwitchResponseFromParser

from .config import TwitchSettings
from .dependencies import get_twitch_parser
from .service import TwitchParser

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]
TwitchDb = Annotated[TwitchDatabaseManager, Depends(get_twitch_database)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]
settings = TwitchSettings()


@twitch_router.post("/streams")
async def parse_streams(
    parser: TwitchParserObject,
    db: TwitchDb,
    cache: CacheMngr,
    first: int = 10,
    game_id: int | None = None,
    language: str = "en",
):
    """This views stands for parsing streams, processed streams are saved to cache and db"""

    query_params = {"first": first, "language": language}
    if game_id is not None:
        query_params["game_id"] = game_id
    key_for_cache = {"twitch_stream_params": query_params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        if object_from_cache["status"] == ObjectStatus.PROCESSED.name:
            return {"message": "object is already processed"}
    streams = list(parser.get_streams(query_params=query_params))
    for stream in streams:
        await db.save_one_stream(stream)
    await cache.save_to_cache(
        key_for_cache,
        60 * 5,
        TwitchResponseFromParser(
            status=ObjectStatus.PROCESSED.name, twitch_streams_params=query_params, data=streams
        ),
    )
    return {"message": "processed"}


@twitch_router.get("/parse/streams", response_model=TwitchResponseFromParser)
async def get_parsed_streams(
    cache: CacheMngr,
    first: int = 10,
    game_id: int | None = None,
    language: str = "en",
):
    """
    This view stands for sending requests for parsing streams
    using kafka, streams are parsed in other application
    """

    query_params = {"first": first, "language": language}
    if game_id is not None:
        query_params["game_id"] = game_id
    key_for_cache = {"twitch_stream_params": query_params}
    object_from_cache = await cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    await cache.save_to_cache(
        key_for_cache,
        60 * 3,
        TwitchResponseFromParser(status=ObjectStatus.PENDING.name, twitch_streams_params=query_params),
    )
    producer.produce(
        settings.twitch_stream_topic,
        key="parse_category",
        value=json.dumps(key_for_cache),
    )
    return TwitchResponseFromParser(
        status=ObjectStatus.CREATED.name, twitch_streams_params=key_for_cache
    )


@twitch_router.get("/test")
async def test_twitch(db: TwitchDb):
    await db.get_test_message("hello")
    return {"message": "success"}
