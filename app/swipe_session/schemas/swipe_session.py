from datetime import date, datetime
from typing import Any, List
from pydantic import BaseModel, validator
from app.swipe_session.schemas.swipe import SwipeSchema
from core.db import session

from core.db.enums import SwipeSessionEnum, SwipeSessionActionEnum
from core.helpers.hashid import encode


class ActionDocsSchema(BaseModel):
    actions: dict


class CreateSwipeSessionSchema(BaseModel):
    status: SwipeSessionEnum = SwipeSessionEnum.READY
    session_date: date | datetime | None = None
    user_id: int = None
    group_id: str | None = None


class UpdateSwipeSessionSchema(BaseModel):
    id: str
    session_date: date = None
    status: SwipeSessionEnum = None
    user_id: int = None


class SwipeSessionSchema(BaseModel):
    id: str
    session_date: date
    status: SwipeSessionEnum
    user_id: str
    group_id: str
    swipes: List[SwipeSchema]

    @validator('id')
    def hash_id(cls, v):
        return encode(int(v))

    @validator('user_id')
    def hash_user_id(cls, v):
        return encode(int(v))

    @validator('group_id')
    def hash_group_id(cls, v):
        return encode(int(v))

    class Config:
        orm_mode = True


class PacketSchema(BaseModel):
    action: SwipeSessionActionEnum
    payload: Any | None = None
