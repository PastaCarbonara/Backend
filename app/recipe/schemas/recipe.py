from pydantic import BaseModel, Field
from app.tag.schemas import Tag


class GetRecipeListResponseSchema(BaseModel):
    recipe_id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    image: str = Field(..., description="Url of image")
    tag: Tag = Field(..., description="Tag")

    class Config:
        orm_mode = True


class JudgeRecipeRequestSchema(BaseModel):
    user_id: int = Field(..., description="userID")
    like: bool = Field(..., description="Of je de recept leuk vindt")

    class Config:
        orm_mode = True
