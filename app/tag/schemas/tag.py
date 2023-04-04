from pydantic import BaseModel, Field


class TagSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="tag name")

    class Config:
        orm_mode = True


class CreateTagSchema(BaseModel):
    name: str
