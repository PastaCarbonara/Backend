from pydantic import BaseModel, Field


class RecipeTagSchema(BaseModel):
    tag_id: int = Field(..., description="Tag ID")

    class Config:
        orm_mode = True
