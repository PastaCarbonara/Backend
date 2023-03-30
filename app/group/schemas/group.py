from dataclasses import Field
from typing import Any
from pydantic import BaseModel, root_validator
from pydantic.utils import GetterDict

from app.user.schemas.user import GetUserListResponseSchema


class CreateGroupSchema(BaseModel):
    name: str

class UserCreateGroupSchema(CreateGroupSchema):
    user_id: int = None


class FlattenedGroupMemberSchema(BaseModel):
    id: int
    username: str
    is_admin: bool

    @root_validator(pre=True)
    def flatten_group_member(clas, values: GetterDict) -> GetterDict | dict[str, object]:
        user = values.get("user")

        if user is None:
            return values
        
        print("WARNING: Currently 'Unknown' is used as default fallback when the user is not logged in.")
        username = "Unknown" if user.profile is None else user.profile.username

        return {
            "id": values["user_id"],
            "username": username,
            "is_admin": values["is_admin"]
        } | dict(values)
    
    class Config:
        orm_mode = True


class GroupSchema(BaseModel):
    id: int
    name: str
    users: list[FlattenedGroupMemberSchema]

    class Config:
        orm_mode = True
