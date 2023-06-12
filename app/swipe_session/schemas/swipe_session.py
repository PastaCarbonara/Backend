from datetime import date
from typing import Any, List
from pydantic import BaseModel
from app.swipe_session.schemas.recipe import RecipeSchema
from app.swipe_session.schemas.swipe import SwipeSchema

from core.db.enums import SwipeSessionEnum, SwipeSessionActionEnum
from core.fastapi.schemas.hashid import DehashId, HashId


class ActionDocsSchema(BaseModel):
    actions: dict


class CreateSwipeSessionSchema(BaseModel):
    status: SwipeSessionEnum = SwipeSessionEnum.READY
    session_date: date | None = None


class UpdateSwipeSessionSchema(BaseModel):
    id: DehashId
    session_date: date = None
    status: SwipeSessionEnum = None


class SwipeSessionSchema(BaseModel):
    id: HashId
    session_date: date
    status: SwipeSessionEnum
    group_id: HashId
    swipes: List[SwipeSchema]
    swipe_match: RecipeSchema = None

    class Config:
        orm_mode = True


class SwipeSessionPacketSchema(BaseModel):
    action: SwipeSessionActionEnum
    payload: Any | None = None
