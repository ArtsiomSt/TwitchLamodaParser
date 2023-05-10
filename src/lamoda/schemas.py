from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class LamodaProduct(BaseModel):
    product_sku: str
    product_type: str
    product_title: str
    brand: str
    created_at: datetime = datetime.utcnow()
    price: Decimal
    attributes: list[dict]
    url: str
