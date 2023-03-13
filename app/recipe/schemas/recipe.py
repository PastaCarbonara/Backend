from typing import List
from pydantic import BaseModel, Field
from .tag import RecipeTagSchema


class GetRecipeListResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    image: str = Field(..., description="Url of image")
    tags: List[RecipeTagSchema] = Field(..., description="Tags of the recipe")

    class Config:
        orm_mode = True


class JudgeRecipeRequestSchema(BaseModel):
    user_id: int = Field(..., description="userID")
    like: bool = Field(..., description="Like the recipe")
