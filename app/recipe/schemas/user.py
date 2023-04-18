from pydantic import BaseModel, Field

from core.fastapi.schemas.hashid import HashId



class UserProfileSchema(BaseModel):
    # user_id: HashId = Field(..., description="ID")
    username: str = Field(..., description="Username")

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    id: HashId = Field(..., description="ID")
    profile: UserProfileSchema | None = Field(None, description="User profile")

    class Config:
        orm_mode = True