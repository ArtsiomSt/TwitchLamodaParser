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
    tags: list[str]


class TwitchStreamParams(BaseModel):
    paginate_by: Optional[int]
    page_num: Optional[int]
    streams_amount: int = 10
    game_id: int = Field(None, gt=0)
    language: str = "en"

    @validator("paginate_by", "page_num", "streams_amount")
    def validate_positive(cls, value):
        if value is not None and value < 0:
            raise PaginationException(detail=f"{value} should be positive")
        return value
