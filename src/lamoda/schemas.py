from typing import Optional

from pydantic import BaseModel, root_validator, Field
from schemas import OID, CustomModel
from .exeptions import NotValidUrlException

from .config import LamodaSettings

settings = LamodaSettings()
lamoda_url = settings.lamoda_url


class LamodaProduct(CustomModel):
    product_sku: str
    product_type: str
    product_title: str
    brand: str
    price: str
    attributes: list[dict]
    category_id: Optional[OID]
    url: str


class LamodaCategory(CustomModel):
    category_title: str
    product_links: list[str]
    url: str
    products: Optional[list[LamodaProduct]]


class LamodaUrl(BaseModel):
    url: str

    @root_validator
    def validate_url(cls, values):
        is_product = values.get("is_product", False)
        is_category = values.get("is_category", False)
        url = values.get("url", "empty")
        if is_product:
            if not url.startswith(lamoda_url + '/p/'):
                raise NotValidUrlException(detail="Not valid url for parsing product")
        elif is_category:
            if not url.startswith(lamoda_url + '/c/'):
                raise NotValidUrlException(detail="Not valid url for parsing category")
        return values


class ProductUrl(LamodaUrl):
    is_product: bool = Field(True, const=True)


class CategoryUrl(LamodaUrl):
    """
    Class for validation url of category, soon mb there
    will be some additional params for url
    """

    is_category: bool = Field(True, const=True)
