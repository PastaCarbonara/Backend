from pydantic import BaseModel, Field


class GetUserListResponseSchema(BaseModel):
    user_id: int = Field(..., description="ID")
    username: str = Field(..., description="Username")

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
    token: str = Field(..., description="Token")
    refresh_token: str = Field(..., description="Refresh token")
