from typing import List

from fastapi import APIRouter, Depends, Query, Request

from app.recipe.schemas import (
    ExceptionResponseSchema,
    JudgeRecipeRequestSchema,
    GetRecipeListResponseSchema,
)
from app.recipe.services import RecipeService
from core.fastapi.dependencies.permission import AllowAll, PermissionDependency


recipe_router = APIRouter()


@recipe_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=List[GetRecipeListResponseSchema],
)
async def get_recipe_list():
    return await RecipeService().get_recipe_list()


@recipe_router.post(
    "{recipe_id}/judge",
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll]))],
)
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema, http_request: Request):
    if http_request.user.id:
        request.user_id = http_request.user.id
        
    await RecipeService().judge_recipe(recipe_id, **request.dict())
    return "Ok"
