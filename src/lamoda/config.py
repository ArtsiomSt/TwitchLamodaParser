from pydantic import BaseSettings


class LamodaSettings(BaseSettings):
    lamoda_url: str

    class Config:
        fields = {
            "lamoda_url": {
                "env": "LAMODA_URL"
            },
        }
