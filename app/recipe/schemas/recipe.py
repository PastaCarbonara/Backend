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
    preparing_time: int = Field(..., description="Time in minutes")

    tags: List[FlattenedRecipeTagSchema] = Field(..., description="Tags of the recipe")
    instructions: List[str] = Field(..., description="Instructions for the recipe")
    ingredients: List[FlattenedRecipeIngredientSchema] = Field(
        ..., description="Ingridients for the recipe"
    )
    judgements: List[JudgementSchema] = Field(
        ..., description="Judgements of the recipe"
    )

    class Config:
        orm_mode = True


class CreateBaseRecipeSchema(BaseModel):
    name: str = Field(..., description="Recipe name")
    description: str | None = Field(None, description="Recipe description")
    preperation_time: int = Field(..., description="Time in minutes")


class CreateRecipeInstructionSchema(BaseModel):
    instruction: str = Field(..., description="Instruction")


class CreateRecipeTagSchema(BaseModel):
    name: str = Field(..., description="Tag name")


class CreateRecipeIngredientSchema(BaseModel):
    name: str = Field(..., description="Ingredient name")
    amount: str = Field(..., description="Ingredient quantity")
    unit: str = Field(..., description="Ingredient unit")


class CreateRecipeBaseRequestSchema(BaseModel):
    name: str = Field(..., description="Recipe name")
    description: str | None = Field(None, description="Recipe description")
    filename: str = Field(..., description="image")
    preparing_time: int = Field(..., description="Time in minutes")

    tags: List[int] = Field(..., description="Tags of the recipe")
    instructions: List[str] = Field(..., description="Instructions for the recipe")
    ingredients: List[CreateRecipeIngredientSchema] = Field(
        ..., description="Ingredients for the recipe"
    )


class UserCreateRecipeRequestSchema(CreateRecipeBaseRequestSchema):
    user_id: int = None


class CreatorCreateRecipeRequestSchema(CreateRecipeBaseRequestSchema):
    creator_id: int = None


class JudgeRecipeRequestSchema(BaseModel):
    user_id: int | None = Field(None, description="UserID, optional")
    like: bool = Field(..., description="Like / Dislike")
