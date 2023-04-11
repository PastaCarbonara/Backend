from typing import Any
from pydantic import BaseModel, Field, validator

from core.helpers.hashid import encode


class GetUserListResponseSchema(BaseModel):
    user_id: int = Field(..., description="ID")
    hashed_id: str = None
    username: str = Field(..., description="Username")

    @validator('hashed_id', always=True)
    def validate_hashed_id(cls, v: str, values: dict[str, Any]) -> str:
        assert "user_id" in values, "sanity check"
        if not v:
            return encode(values["user_id"])
    
    class Config:
        orm_mode = True


class CreateUserRequestSchema(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class CreateUserResponseSchema(BaseModel):
    username: str = Field(..., description="Username")

    class Config:
        orm_mode = True


class LoginResponseSchema(BaseModel):
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
