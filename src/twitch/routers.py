from typing import Annotated

from fastapi import APIRouter, Depends

from db import get_twitch_database
from db.database_managers import TwitchDatabaseManager
from .dependencies import get_twitch_parser
from .service import TwitchParser
from .schemas import TwitchStream

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]
TwitchDb = Annotated[TwitchDatabaseManager, Depends(get_twitch_database)]


@twitch_router.get("/streams")
def parse_streams(
    parser: TwitchParserObject,
    db: TwitchDb,
    first: int = 10,
    game_id: int | None = None,
    language: str = "en",
) -> list[TwitchStream]:
    query_params = {"first": first, "language": language}
    if game_id is not None:
        query_params["game_id"] = game_id
    streams = list(parser.get_streams(query_params=query_params))
    for stream in streams:
        db.save_one_stream(stream)
    return streams


@twitch_router.get("/test")
def test_twitch(db: TwitchDb):
    db.get_test_message("hello")
    return {"message": "success"}
