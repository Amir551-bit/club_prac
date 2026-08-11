from sqlite.redis_client import redis_client
from core.execptions.execption import raise_bad_request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json




def create_or_update_to_api_redis(locked_key: str):
    is_locked = redis_client.set(locked_key, "lock", ex=6, nx=True)
    if not is_locked:
        raise_bad_request("در حال پردازش است لطفا صبور باشید.")


def get_for_redis(cache_key: str, get_responses: BaseModel, db_fetch_function):
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # فقط زمانی که کش نبود، تابعِ دیتابیس اجرا می‌شود!
    if callable(db_fetch_function):
        data = db_fetch_function()
    else:
        data = db_fetch_function
    
    response_model_obj = get_responses.model_validate(data)
    not_dict_data = response_model_obj.model_dump()
    not_json_data = response_model_obj.model_dump_json()
    redis_client.setex(cache_key, 600, not_json_data)
    return not_dict_data

def commit(obj, db: Session):
    db.add(obj)
    db.commit()
    db.refresh(obj)

def update(obj, db:Session):
    db.commit()
    db.refresh(obj)


def delete(obj, db: Session):
    db.delete(obj)
    db.commit()


def commit_notification(obj, db: Session):
    db.add(obj)
    db.commit()