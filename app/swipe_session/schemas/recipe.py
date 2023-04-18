from pydantic import BaseModel, Field

from app.image.schemas.image import ImageSchema


class RecipeSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    image: ImageSchema = Field(..., description="Image ")

    class Config:
        orm_mode = True