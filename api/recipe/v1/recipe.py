from typing import List

from fastapi import APIRouter, Depends, Query, Request

from app.recipe.schemas import (
    ExceptionResponseSchema,
    JudgeRecipeRequestSchema,
    GetRecipeListResponseSchema,
    GetFullRecipeResponseSchema,
    CreateRecipeRequestSchema,
)
from app.recipe.services import RecipeService
from core.fastapi.dependencies.permission import AllowAll, PermissionDependency, ProvidesUserID, IsAdmin
from core.exceptions.user import MissingUserIDException


recipe_router = APIRouter()


@recipe_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=List[GetRecipeListResponseSchema],
)
async def get_recipe_list():
    return await RecipeService().get_recipe_list()


@recipe_router.put(
    "/{recipe_id}/judge",
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll, ProvidesUserID]))],
)
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema, http_request: Request):
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
