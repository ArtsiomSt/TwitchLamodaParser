from fastapi import HTTPException


class NotValidUrlException(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=400,
            detail="Not valid url for parsing" if detail is None else detail,
        )
