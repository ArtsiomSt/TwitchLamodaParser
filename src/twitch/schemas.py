from typing import Optional

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
    game_id: int
    game_name: str
    stream_title: str
    viewer_count: int
    tags: list[str]
