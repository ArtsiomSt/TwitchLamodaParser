from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, root_validator

from exceptions import PaginationException


class OID(str):
    """
    Class that helps with refactoring id from
    ObjectID to str while creating instance
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v == "":
            raise TypeError("ObjectId is empty")
        if not ObjectId.is_valid(v):
            raise TypeError("ObjectId invalid")
        return str(v)


class CustomModel(BaseModel):
    id: Optional[OID]
    created_at: datetime = datetime.utcnow()


class PaginateFields(BaseModel):
    paginate_by: Optional[int] = Field(10, gt=-1, le=20)
    page_num: Optional[int] = Field(0, gt=-1)

    @root_validator
    def validate_pagination(cls, values):
        paginate_by = values.get("paginate_by", None)
        page_num = values.get("page_num", None)
        if (page_num is None and paginate_by is not None) or (
            page_num is not None and paginate_by is None
        ):
            raise PaginationException(
                detail="You have to provide both page_num and paginate_by"
            )
        return values


class ResponseFromDb(PaginateFields):
    status: str
    data: Any
