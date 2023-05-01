from typing import Any
from pydantic import BaseModel, Field, validator
from core.fastapi.schemas import HashId


class AccountAuthSchema(BaseModel):
    username: str = Field(..., description="Username")
    
    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    id: HashId
    display_name: str
    is_admin: bool
    account_auth: AccountAuthSchema = None
    
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
