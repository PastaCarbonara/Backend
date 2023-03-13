from typing import List
from pydantic import BaseModel, Field
from .tag import RecipeTagSchema


class GetRecipeListResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    image: str = Field(..., description="Image url")
    tags: List[RecipeTagSchema] = Field(..., description="Recipe tags")

    class Config:
        orm_mode = True


class JudgeRecipeRequestSchema(BaseModel):
    user_id: int | None = Field(None, description="UserID, optional")
    like: bool = Field(..., description="Like / Dislike")
