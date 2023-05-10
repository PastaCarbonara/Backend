from pydantic import BaseModel, Field
from core.db.enums import TagType

class FilterSchema(BaseModel):
    id: int = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")
    tag_type: TagType = Field(..., description="Type of filter")

    class Config:
        orm_mode = True

class AdminCreateSchema(BaseModel):
    user_id: int = Field(..., description="User ID")
    tags: list[int] = Field(..., description="Tag ID")

class UserCreateSchema(BaseModel):
    tags: list[int] = Field(..., description="Tag ID")
