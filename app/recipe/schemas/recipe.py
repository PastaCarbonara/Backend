from typing import List
from pydantic import BaseModel, Field

from .judgement import JudgementSchema

# from .instruction import InstructionItemSchema
# from .ingredient import GetIngredientSchema, IngredientSchema
from .user import UserSchema
from .tag import RecipeTagSchema, FlattendRecipeTagSchema


class GetRecipeListResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    image: str = Field(..., description="Image url")
    tags: List[RecipeTagSchema] = Field(..., description="Recipe tags")

    class Config:
        orm_mode = True


class GetFullRecipeResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    name: str = Field(..., description="Recipe name")
    description: str | None = Field(None, description="Recipe description")
    image: str = Field(..., description="Url of image")
    creator: UserSchema = Field(..., description="Creator of the recipe")
    preparing_time: int = Field(..., description="Time in minutes")

    tags: List[FlattendRecipeTagSchema] = Field(..., description="Tags of the recipe")
    instructions: List[str] = Field(..., description="Instructions for the recipe")
    ingredients: List[str] = Field(..., description="Ingridients for the recipe")
    # judgements: List[JudgementSchema] = Field(
    #     ..., description="Judgements of the recipe"
    # )

    class Config:
        orm_mode = True


class CreateRecipeBaseRequestSchema(BaseModel):
    name: str = Field(..., description="Recipe name")
    description: str | None = Field(None, description="Recipe description")
    image: str = Field(..., description="Url of image")
    preparing_time: int = Field(..., description="Time in minutes")

    tags: List[RecipeTagSchema] = Field(..., description="Tags of the recipe")
    instructions: List[str] = Field(..., description="Instructions for the recipe")
    ingredients: List[str] = Field(..., description="Ingridients for the recipe")


class UserCreateRecipeRequestSchema(CreateRecipeBaseRequestSchema):
    user_id: int = None


class CreatorCreateRecipeRequestSchema(CreateRecipeBaseRequestSchema):
    creator_id: int = None


class JudgeRecipeRequestSchema(BaseModel):
    user_id: int | None = Field(None, description="UserID, optional")
    like: bool = Field(..., description="Like / Dislike")
