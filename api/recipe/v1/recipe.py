from typing import List

from fastapi import APIRouter, Depends, Query, Request
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version

from app.recipe.schemas import (
    JudgeRecipeRequestSchema,
    GetRecipeListResponseSchema,
    GetFullRecipeResponseSchema,
    UserCreateRecipeRequestSchema,
    CreatorCreateRecipeRequestSchema,
)
from app.recipe.services import RecipeService
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    ProvidesUserID,
    IsAdmin,
)


recipe_v1_router = APIRouter()


@recipe_v1_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=List[GetFullRecipeResponseSchema],
)
@version(1)
async def get_recipe_list():
    return await RecipeService().get_full_recipe_list()


@recipe_v1_router.get(
    "/{recipe_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GetFullRecipeResponseSchema,
)
@version(1)
async def get_recipe_by_id(recipe_id: int):
    return await RecipeService().get_recipe_by_id(recipe_id)


@recipe_v1_router.put(
    "/{recipe_id}/judge",
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll, ProvidesUserID]))],
)
@version(1)
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema):
    await RecipeService().judge_recipe(recipe_id, **request.dict())
    return "Ok"


@recipe_v1_router.post(
    "",
    response_model=GetFullRecipeResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin, ProvidesUserID]))],
)
@version(1)
async def create_recipe(request: UserCreateRecipeRequestSchema):
    recipe_id = await RecipeService().create_recipe(
        CreatorCreateRecipeRequestSchema(creator_id=request.user_id, **request.dict())
    )
    return await RecipeService().get_recipe_by_id(recipe_id)
