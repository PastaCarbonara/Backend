from dataclasses import Field
from typing import Any
from pydantic import BaseModel, root_validator, validator
from pydantic.utils import GetterDict
from app.recipe.schemas.user import UserSchema


from core.fastapi.schemas.hashid import HashId
from core.helpers.hashid import encode


class CreateGroupSchema(BaseModel):
    name: str


class FlattenedGroupMemberSchema(BaseModel):
    id: HashId
    username: str
    is_admin: bool
    # user: UserSchema = None

    @root_validator(pre=True)
    def flatten_group_member(cls, values: GetterDict) -> GetterDict | dict[str, object]:
        user = values.get("user")

        if user is None:
            return values
        
        # NOTE: Currently 'Unknown' is used as default fallback when the user is not registered.. if that is possible.
        if not user.profile:
            user.profile.username = "Unknown"

        return {
            "id": user.id,
            "username": user.profile.username,
            "is_admin": values["is_admin"],
            "user": None,
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
