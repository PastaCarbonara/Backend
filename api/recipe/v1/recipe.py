"""Endpoints for recipe.
"""
from fastapi import APIRouter, Depends
from core.exceptions import ExceptionResponseSchema
from core.fastapi.dependencies.user import get_current_user
from core.fastapi_versioning import version
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    IsAuthenticated,
)

from app.recipe.schemas import (
    JudgeRecipeSchema,
    GetFullRecipeResponseSchema,
    GetFullRecipePaginatedResponseSchema,
    CreateRecipeSchema,
)
from app.recipe.services import RecipeService



recipe_v1_router = APIRouter()


@recipe_v1_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GetFullRecipePaginatedResponseSchema,
)
@version(1)
async def get_recipe_list(limit: int = 10, offset: int = 0):
    # return {"total_count": 0, "recipes": []}
    return await RecipeService().get_paginated_recipe_list(limit, offset)



@recipe_v1_router.get(
    "/{recipe_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GetFullRecipeResponseSchema,
)
@version(1)
async def get_recipe_by_id(recipe_id: int):
    return await RecipeService().get_recipe_by_id(recipe_id)


@recipe_v1_router.post(
    "/{recipe_id}/judge",
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def judge_recipe(
    recipe_id: int, request: JudgeRecipeSchema, user=Depends(get_current_user)
):
    await RecipeService().judge_recipe(recipe_id, user.id, request.like)
    return "Ok"


@recipe_v1_router.post(
    "",
    response_model=GetFullRecipeResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def create_recipe(request: CreateRecipeSchema, user=Depends(get_current_user)):
    recipe_id = await RecipeService().create_recipe(request, user.id)
    return await RecipeService().get_recipe_by_id(recipe_id)


# @recipe_v1_router.put(
#     "/{recipe_id}",
#     response_model=GetFullRecipeResponseSchema,
#     responses={"400": {"model": ExceptionResponseSchema}},
#     dependencies=[Depends(PermissionDependency([[IsAuthenticated, ProvidesUserID]]))],
# )
# @version(1)
# async def update_recipe(recipe_id: int, request: UserCreateRecipeRequestSchema):
#     await RecipeService().update_recipe(recipe_id, request)
#     return await RecipeService().get_recipe_by_id(recipe_id)


# @recipe_v1_router.delete(
#     "/{recipe_id}",
#     responses={"400": {"model": ExceptionResponseSchema}},
#     status_code=204,
#     dependencies=[Depends(PermissionDependency([[IsAuthenticated, ProvidesUserID]]))],
# )
# @version(1)
# async def delete_recipe(recipe_id: int):
#     await RecipeService().delete_recipe(recipe_id)
#     return {"message": "Recipe deleted successfully."}
