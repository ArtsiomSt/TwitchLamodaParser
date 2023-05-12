from typing import Annotated

from fastapi import APIRouter, Depends

from .dependencies import get_twitch_parser
from .service import TwitchParser

twitch_router = APIRouter(prefix="/twitch")


TwitchParserObject = Annotated[TwitchParser, Depends(get_twitch_parser)]


@twitch_router.get("/streams")
def parse_streams(parser: TwitchParserObject):
    parser.get_streams()
    return {"message": "success"}
