from fastapi import APIRouter

from lamoda.utils import parse_object

lamoda_router = APIRouter(prefix='/lamoda')


@lamoda_router.post("/product")
def parse_product(url: str):
    """View for parsing product by its url"""

    return parse_object(url).dict()


@lamoda_router.get("/")
def main_page():
    return {"message": "success"}
