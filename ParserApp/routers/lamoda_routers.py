from fastapi import APIRouter

from parsers.lamoda_parsers import parse_category, parse_object
from settings.db import lamoda_collection

lamoda_router = APIRouter()


@lamoda_router.post("/product")
def parse_product(url: str):
    """View for parsing product by its url"""

    return parse_object(url).dict()


@lamoda_router.get("/")
def main_page():
    return {"message": "success"}
