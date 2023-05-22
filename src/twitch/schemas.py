from typing import Optional

from pydantic import BaseModel, Field, validator

from exceptions import PaginationException
from schemas import CustomModel


class TwitchUser(CustomModel):
    user_id: str
    login: str
    display_name: str
    type: str
    description: str
    type: str
    view_count: int
    broadcaster_type: str
    email: Optional[str]


class TwitchStream(CustomModel):
    twitch_id: int
    user: TwitchUser
    game_id: int | str
    game_name: str
    stream_title: str
    viewer_count: int
    tags: Optional[list[str]]


class TwitchStreamParams(BaseModel):
    paginate_by: Optional[int] = Field(gt=0)
    page_num: Optional[int] = Field(gt=0)
    streams_amount: int = Field(10, gt=0)
    game_id: int = Field(None, gt=0)
    language: str = "en"
