from pydantic import BaseSettings


class TwitchSettings(BaseSettings):
    client_id: str
    client_secret: str
    grand_type: str
    token_url: str
    streams_url: str
    users_url: str
    games_url: str

    class Config:
        fields = {
            "client_id": {
                "env": "CLIENT_ID",
            },
            "token_url": {
                "env": "TOKEN_URL",
            },
            "grand_type": {"env": "GRAND_TYPE"},
            "client_secret": {"env": "client_secret"},
            "streams_url": {"env": "GET_STREAMS"},
            "users_url": {"env": "GET_USERS"},
            "games_url": {"env": "GET_GAMES"}
        }
