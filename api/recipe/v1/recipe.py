from typing import List

from fastapi import APIRouter, Depends, Query

from app.recipe.schemas import JudgeRecipeRequestSchema, GetRecipeListResponseSchema
from app.recipe.services import RecipeService


recipe_router = APIRouter()


@recipe_router.get("", response_model=List[GetRecipeListResponseSchema])
async def get_recipe_list():
    return await RecipeService().get_recipe_list()


@recipe_router.post("{recipe_id}/judge")
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema):
    await RecipeService().judge_recipe(recipe_id, **request.dict())
    return "Ok"
