import requests
from fastapi.exceptions import HTTPException

from .config import TwitchSettings

settings = TwitchSettings()


class TwitchParser:
    def __init__(self):
        token_info = self.obtain_access_token()
        self.access_token = token_info.get("access_token", None)
        self.token_type = token_info.get("token_type", None)
        self.client_id = settings.client_id

    @staticmethod
    def obtain_access_token() -> dict:
        token_params = {
            "client_id": settings.client_id,
            "client_secret": settings.client_secret,
            "grant_type": settings.grand_type,
        }
        token_url = settings.token_url
        response = requests.post(token_url, params=token_params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="unable to use twitch api")
        return response.json()

    def send_request(self, url: str) -> dict:
        if self.access_token is None:
            raise HTTPException(status_code=500, detail="unable to use twitch api")
        headers = {
            "Authorization": f"{self.token_type.capitalize()} {self.access_token}",
            "Client-ID": self.client_id,
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="problems with twitch api")
        return response.json()

    def get_streams(self):
        stream_url = settings.streams_url
        response = self.send_request(stream_url)
        return response
