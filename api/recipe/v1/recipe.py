from typing import List

from fastapi import APIRouter, Depends, Query

from app.recipe.schemas import (
    JudgeRecipeRequestSchema,
    GetRecipeListResponseSchema,
    GetFullRecipeResponseSchema,
    CreateRecipeRequestSchema,
)
from app.recipe.services import RecipeService
from app.user.schemas import ExceptionResponseSchema
from core.fastapi.dependencies.permission import IsAdmin, PermissionDependency


recipe_router = APIRouter()


@recipe_router.get("", response_model=List[GetRecipeListResponseSchema])
async def get_recipe_list():
    return await RecipeService().get_recipe_list()


@recipe_router.put("{recipe_id}/judge")
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema):
    await RecipeService().judge_recipe(recipe_id, **request.dict())
    return "Ok"


@recipe_router.post(
    "",
    response_model=GetFullRecipeResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
async def create_recipe(recipe: CreateRecipeRequestSchema):
    print(recipe)
