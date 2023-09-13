from pydantic import BaseSettings


class LamodaSettings(BaseSettings):
    lamoda_url: str
    lamoda_products_topic: str
    lamoda_category_topic: str

    class Config:
        fields = {
            "lamoda_url": {"env": "LAMODA_URL"},
            "lamoda_products_topic": {"env": "LAMODA_PRODUCT_TOPIC"},
            "lamoda_category_topic": {"env": "LAMODA_CATEGORY_TOPIC"},
        }
