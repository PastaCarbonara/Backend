from typing import Any
from pydantic import BaseModel, Field, validator
from core.fastapi.schemas import HashId


class UserProfileSchema(BaseModel):
    username: str = Field(..., description="Username")
    is_admin: bool
    
    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    id: HashId
    profile: UserProfileSchema | None = None
    
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
