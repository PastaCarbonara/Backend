from typing import List

from fastapi import APIRouter, Depends, Query, Request

from app.recipe.schemas import (
    ExceptionResponseSchema,
    JudgeRecipeRequestSchema,
    GetRecipeListResponseSchema,
    GetFullRecipeResponseSchema,
    UserCreateRecipeRequestSchema,
    CreatorCreateRecipeRequestSchema,
)
from app.recipe.services import RecipeService
from core.fastapi.dependencies.permission import AllowAll, PermissionDependency, ProvidesUserID, IsAdmin


recipe_router = APIRouter()


@recipe_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=List[GetRecipeListResponseSchema],
)
async def get_recipe_list():
    return await RecipeService().get_recipe_list()


@recipe_router.get(
    "/{recipe_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GetFullRecipeResponseSchema,
)
async def get_recipe_by_id(recipe_id: int):
    return await RecipeService().get_recipe_by_id(recipe_id)


@recipe_router.put(
    "/{recipe_id}/judge",
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll, ProvidesUserID]))],
)
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema):
    await RecipeService().judge_recipe(recipe_id, **request.dict())
    return "Ok"


@recipe_router.post(
    "",
    response_model=GetFullRecipeResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin, ProvidesUserID]))],
)
async def create_recipe(request: UserCreateRecipeRequestSchema):
    recipe_id = await RecipeService().create_recipe(CreatorCreateRecipeRequestSchema(
        creator_id=request.user_id,
        **request.dict()
    ))
    return await RecipeService().get_recipe_by_id(recipe_id)
