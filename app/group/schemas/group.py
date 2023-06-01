from typing import Optional
from pydantic import Field
from pydantic import BaseModel, root_validator
from pydantic.utils import GetterDict
from app.image.schemas.image import ImageSchema
from app.swipe_session.schemas.swipe_session import SwipeSessionSchema


from core.fastapi.schemas.hashid import HashId

# pylint : disable=no-self-argument


class CreateGroupSchema(BaseModel):
    name: str = Field(..., max_length=100)
    filename: str


class FlattenedGroupMemberSchema(BaseModel):
    id: HashId
    display_name: str
    image: ImageSchema = None
    is_admin: bool

    @root_validator(pre=True)
    def flatten_group_member(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        user = values.get("user")

        if user is None:
            return values

        return {
            "id": user.id,
            "display_name": user.display_name,
            "image": user.image,
            "is_admin": values["is_admin"],
            "user": None,
        } | dict(values)

    class Config:
        orm_mode = True


class GroupSchema(BaseModel):
    id: HashId
    name: str
    image: ImageSchema = Field(..., description="image")
    users: list[FlattenedGroupMemberSchema]
    swipe_sessions: list[SwipeSessionSchema]

    class Config:
        orm_mode = True


class GroupInfoSchema(BaseModel):
    id: HashId
    name: str
    image: ImageSchema = Field(..., description="image")
    users: list[FlattenedGroupMemberSchema]

    class Config:
        orm_mode = True
