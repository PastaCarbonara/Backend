from pydantic import Field
from typing import Any
from pydantic import BaseModel, root_validator, validator
from pydantic.utils import GetterDict
from app.swipe_session.schemas.swipe_session import SwipeSessionSchema


from core.fastapi.schemas.hashid import HashId


class CreateGroupSchema(BaseModel):
    name: str = Field(..., max_length=100)
    filename: str


class FlattenedGroupMemberSchema(BaseModel):
    id: HashId
    display_name: str
    is_admin: bool

    @root_validator(pre=True)
    def flatten_group_member(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        user = values.get("user")

        if user is None:
            return values

        return {
            "id": user.id,
            "display_name": user.display_name,
            "is_admin": values["is_admin"],
            "user": None,
        } | dict(values)
    
    class Config:
        orm_mode = True


class GroupSchema(BaseModel):
    id: HashId
    name: str
    filename: str
    users: list[FlattenedGroupMemberSchema]
    swipe_sessions: list[SwipeSessionSchema]

    class Config:
        orm_mode = True
