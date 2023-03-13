from pydantic import BaseModel, Field



class UserProfileSchema(BaseModel):
    # user_id: int = Field(..., description="ID")
    username: str = Field(..., description="Username")

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    id: int = Field(..., description="ID")
    profile: UserProfileSchema | None = Field(None, description="User profile")

    class Config:
        orm_mode = True