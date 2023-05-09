from fastapi import APIRouter

from parsers.lamoda_parsers import parse_category, parse_object

lamoda_router = APIRouter()


@lamoda_router.post("/product")
def parse_product(url: str):
    return parse_object(url)
