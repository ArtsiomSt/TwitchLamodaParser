from typing import Annotated

from fastapi import APIRouter, Depends

from .dependencies import get_twitch_parser
from .service import TwitchParser

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]


@twitch_router.get("/streams")
def parse_streams(
    parser: TwitchParserObject,
    first: int = 10,
    game_id: int | None = None,
    language: str = "en",
):
    query_params = {"first": first, "language": language}
    if game_id is not None:
        query_params["game_id"] = game_id
    streams = list(parser.get_streams(query_params=query_params))
    return streams
