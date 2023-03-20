from typing import List
from pydantic import BaseModel
from app.swipe_session.schemas.swipe import SwipeSchema

from core.db.enums import SwipeSessionEnum


class CreateSwipeSessionSchema(BaseModel):
    status: SwipeSessionEnum = SwipeSessionEnum.IN_PROGRESS
    user_id: int = None


class SwipeSessionSchema(BaseModel):
    id: int
    status: SwipeSessionEnum
    user_id: int
    swipes: List[SwipeSchema]

    class Config:
        orm_mode = True
