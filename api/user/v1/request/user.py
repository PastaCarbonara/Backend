from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Email")
    password: str = Field(..., description="Password")
