from pydantic import BaseModel, Field


class Tag(BaseModel):
    tag_id: int = Field(..., description="ID")
    name: str = Field(..., description="tag name")

    class Config:
        orm_mode = True
