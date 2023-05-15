import json
from datetime import datetime

from redis import Redis
from config import Settings
from typing import Any
from pydantic import BaseModel

settings = Settings()


class RedisCacheManager:
    def __init__(self):
        self.redis = Redis(host="redis", port=6379)
        self.is_active = True

    def save_to_cache(self, key: Any,  ttl: int, value: Any) -> bool:
        if isinstance(value, BaseModel) or isinstance(value, dict):
            dict_from_object = value.dict() if isinstance(value, BaseModel) else value
            replace_basemodel_unserializable_fields(dict_from_object)
            print(dict_from_object)
            value = dict_from_object
        value = json.dumps(value).encode("utf-8")
        return self.redis.setex(json.dumps(key).encode("utf-8"), ttl, value)

    def get_object_from_cache(self, key: Any) -> Any:
        value = self.redis.get(json.dumps(key).encode("utf-8"))
        if value:
            try:
                return json.loads(value.decode())
            except json.decoder.JSONDecodeError:
                return value.decode()
        return None


def replace_basemodel_unserializable_fields(dict_from_object: dict):
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
                    print(dict_from_current_object)
                    new_list.append(dict_from_current_object)
            dict_from_object[dkey] = new_list
        elif isinstance(dvalue, dict):
            replace_basemodel_unserializable_fields(dvalue)
