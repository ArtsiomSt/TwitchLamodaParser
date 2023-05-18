import json
from datetime import datetime
from typing import Any

from aioredis import Redis
from pydantic import BaseModel

from config import Settings

settings = Settings()


class RedisCacheManager:
    """
    Class for providing saving info to redis,
    it checks and provide custom keys(dicts for ex),
    also checks if there are fields that can not be
    serialized and saved to redis
    """

    def __init__(self):
        self.redis = Redis(host=settings.redis_host, port=int(settings.redis_port))
        self.is_active = True

    async def save_to_cache(self, key: Any, ttl: int, value: Any) -> bool:
        if isinstance(value, BaseModel) or isinstance(value, dict):
            dict_from_object = value.dict() if isinstance(value, BaseModel) else value
            replace_basemodel_unserializable_fields(dict_from_object)
            value = dict_from_object
        value = json.dumps(value).encode("utf-8")
        return await self.redis.setex(json.dumps(key).encode("utf-8"), ttl, value)

    async def get_object_from_cache(self, key: Any) -> Any:
        value = await self.redis.get(json.dumps(key).encode("utf-8"))
        if value:
            try:
                return json.loads(value.decode())
            except json.decoder.JSONDecodeError:
                return value.decode()
        return None


def replace_basemodel_unserializable_fields(dict_from_object: dict):
    """
    Checks and replaces fields that can not be serialized
    (for ex. datetime field in BaseModel)
    """

    for dkey, dvalue in dict_from_object.items():
        if isinstance(dvalue, datetime):
            dict_from_object[dkey] = str(dvalue)
        elif isinstance(dvalue, list):
            new_list = []
            for list_inst in dvalue:
                if isinstance(list_inst, dict):
                    replace_basemodel_unserializable_fields(list_inst)
                    new_list.append(list_inst)
                if isinstance(list_inst, BaseModel):
                    dict_from_current_object = list_inst.dict()
                    replace_basemodel_unserializable_fields(dict_from_current_object)
                    new_list.append(dict_from_current_object)
            dict_from_object[dkey] = new_list
        elif isinstance(dvalue, dict):
            replace_basemodel_unserializable_fields(dvalue)
