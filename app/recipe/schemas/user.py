from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int = Field(..., description="ID")
    username: str = Field(..., description="Username")

    class Config:
        orm_mode = True