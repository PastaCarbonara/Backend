from typing import List
from pydantic import BaseModel, Field
from app.user.schemas import UserSchema
from app.image.schemas import ImageSchema
from .judgement import JudgementSchema
from .tag import RecipeTagSchema, FlattenedRecipeTagSchema
from .ingredient import CreateRecipeIngredientSchema, FlattenedRecipeIngredientSchema


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
    likes: int = Field(..., description="Likes of the recipe")

    class Config:
        orm_mode = True

class GetFullRecipePaginatedResponseSchema(BaseModel):
    total_count: int = Field(..., description="Total amount of recipes")
    recipes: List[GetFullRecipeResponseSchema] = Field(..., description="Recipes")
    

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
