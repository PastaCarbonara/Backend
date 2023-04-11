from dataclasses import Field
from typing import Any
from pydantic import BaseModel, root_validator, validator
from pydantic.utils import GetterDict


from app.user.schemas.user import GetUserListResponseSchema
from core.helpers.hashid import encode


class CreateGroupSchema(BaseModel):
    name: str


class FlattenedGroupMemberSchema(BaseModel):
    id: str
    username: str
    is_admin: bool

    @root_validator(pre=True)
    def flatten_group_member(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        user = values.get("user")

        if user is None:
            return values
        
        # NOTE: Currently 'Unknown' is used as default fallback when the user is not registered.. if that is possible.
        username = "Unknown" if user.profile is None else user.profile.username

        return {
            "id": encode(values["user_id"]),
            "username": username,
            "is_admin": values["is_admin"]
        } | dict(values)
    
    class Config:
        orm_mode = True


class GroupSchema(BaseModel):
    id: str
    name: str
    users: list[FlattenedGroupMemberSchema]

    @validator('id')
    def hash_id(cls, v):
        return encode(int(v))

    class Config:
        orm_mode = True
