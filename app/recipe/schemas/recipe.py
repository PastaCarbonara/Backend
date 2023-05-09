from typing import List
from pydantic import BaseModel, Field

from .judgement import JudgementSchema

from .user import UserSchema
from .tag import RecipeTagSchema, FlattenedRecipeTagSchema
from .ingredient import CreateRecipeIngredientSchema, FlattenedRecipeIngredientSchema
from app.image.schemas import ImageSchema


class GetRecipeListResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    image: ImageSchema = Field(..., description="Image ")
    tags: List[RecipeTagSchema] = Field(..., description="Recipe tags")

    class Config:
        orm_mode = True


class GetFullRecipeResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    description: str | None = Field(None, description="Recipe description")
    image: ImageSchema = Field(..., description="image")
    creator: UserSchema = Field(..., description="Creator of the recipe")
    preparation_time: int = Field(..., description="Time in minutes")

    tags: List[FlattenedRecipeTagSchema] = Field(..., description="Tags of the recipe")
    instructions: List[str] = Field(..., description="Instructions for the recipe")
    materials: List[str] | None = Field(..., description="Materials for the recipe")
    ingredients: List[FlattenedRecipeIngredientSchema] = Field(
        ..., description="Ingridients for the recipe"
    )
    judgements: List[JudgementSchema] = Field(
        ..., description="Judgements of the recipe"
    )

    class Config:
        orm_mode = True


class CreateRecipeSchema(BaseModel):
    name: str = Field(..., description="Recipe name")
    description: str | None = Field(None, description="Recipe description")
    filename: str = Field(..., description="image")
    preparation_time: int = Field(..., description="Time in minutes")

    tags: List[str] = Field(..., description="Tags of the recipe")
    instructions: List[str] = Field(..., description="Instructions for the recipe")
    materials: List[str] = Field(None, description="Materials for the recipe")
    ingredients: List[CreateRecipeIngredientSchema] = Field(
        ..., description="Ingredients for the recipe"
    )


class JudgeRecipeSchema(BaseModel):
    like: bool = Field(..., description="Like / Dislike")
