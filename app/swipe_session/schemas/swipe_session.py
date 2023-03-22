from typing import Any, List
from pydantic import BaseModel, validator
from app.swipe_session.schemas.swipe import SwipeSchema
from core.db import session

from core.db.enums import SwipeSessionEnum, SwipeSessionActionEnum
from core.helpers.hashids import encode


class ActionDocsSchema(BaseModel):
    actions: dict


class CreateSwipeSessionSchema(BaseModel):
    status: SwipeSessionEnum = SwipeSessionEnum.IN_PROGRESS
    user_id: int = None


class SwipeSessionSchema(BaseModel):
    id: int
    hashed_id: str = None
    status: SwipeSessionEnum
    user_id: int
    swipes: List[SwipeSchema]

    @validator('hashed_id', always=True)
    def validate_hashed_id(cls, v: str, values: dict[str, Any]) -> str:
        assert "id" in values, "sanity check"
        if not v:
            return encode(values["id"])
        return v

    class Config:
        orm_mode = True


class PacketSchema(BaseModel):
    action: SwipeSessionActionEnum
    payload: Any | None = None
