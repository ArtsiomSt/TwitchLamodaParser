from typing import Annotated

from fastapi import APIRouter, Depends

from cache import RedisCacheManager
from db import get_twitch_database
from db.database_managers import TwitchDatabaseManager
from dependecies import get_cache_manager
from .dependencies import get_twitch_parser
from .service import TwitchParser
from .schemas import TwitchStream

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]
TwitchDb = Annotated[TwitchDatabaseManager, Depends(get_twitch_database)]
CacheMngr = Annotated[RedisCacheManager, Depends(get_cache_manager)]


@twitch_router.get("/streams")
def parse_streams(
    parser: TwitchParserObject,
    db: TwitchDb,
    cache: CacheMngr,
    first: int = 10,
    game_id: int | None = None,
    language: str = "en",
):
    """This views stands for parsing streams"""

    query_params = {"first": first, "language": language}
    if game_id is not None:
        query_params["game_id"] = game_id
    key_for_cache = {"twitch_stream_params": query_params}
    object_from_cache = cache.get_object_from_cache(key_for_cache)
    if object_from_cache:
        return object_from_cache
    streams = list(parser.get_streams(query_params=query_params))
    for stream in streams:
        db.save_one_stream(stream)
    cache_values = {"data": streams}
    cache.save_to_cache(key_for_cache, 20, cache_values)
    return streams


@twitch_router.get("/test")
def test_twitch(db: TwitchDb):
    db.get_test_message("hello")
    return {"message": "success"}
