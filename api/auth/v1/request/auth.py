import uuid
from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")


class VerifyTokenRequest(BaseModel):
    token: str = Field(..., description="Token")


class LoginRequest(BaseModel):
    username: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class ClientTokenSchema(BaseModel):
    token: str


class UUIDSchema(BaseModel):
    token: uuid.UUID | str
