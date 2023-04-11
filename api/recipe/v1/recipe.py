"""Endpoints for recipe.
Paths:
"" - GET - Get a list of all recipes.
"" - POST - Create a recipe basic information(name, description, preparation time).
"/{recipe_id}" - GET - Get a recipe by id.
"/{recipe_id}" - PUT - Update primary information(name, description, preparation time) of the recipe.
"/{recipe_id}" - DELETE - Delete a recipe.
"/{recipe_id}/steps" - POST - Add/Update steps to a recipe.
"/{recipe_id}/images" - POST - Add images to a recipe.
"/{recipe_id}/images/{filename}" - DELETE - Remove an image from a recipe.
"/{recipe_id}/ingredients" - POST - Add ingredients to a recipe.
"/{recipe_id}/ingredients/{ingredient_id}" - DELETE - Remove an ingredient from a recipe.
"/{recipe_id}/ingredients/{ingredient_id}" - PUT - Update an ingredient of a recipe.
"/{recipe_id}/tags" - POST - Add tags to a recipe.
"/{recipe_id}/tags/{tag_id}" - DELETE - Remove a tag from a recipe.
"/{recipe_id}/tags/{tag_id}" - PUT - Update a tag of a recipe.
"/{recipe_id}/judge" - POST - Like or dislike a recipe.
"""

from typing import List

from fastapi import APIRouter, Depends
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version

from app.recipe.schemas import (
    JudgeRecipeRequestSchema,
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
    return await RecipeService().get_recipe_list()


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
    dependencies=[Depends(PermissionDependency([[AllowAll, ProvidesUserID]]))],
)
@version(1)
async def judge_recipe(recipe_id: int, request: JudgeRecipeRequestSchema):
    print(request.user_id)
    return await RecipeService().judge_recipe(recipe_id, request.user_id, request.like)


@recipe_v1_router.post(
    "",
    response_model=GetFullRecipeResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin, ProvidesUserID]]))],
)
@version(1)
async def create_recipe(request: UserCreateRecipeRequestSchema):
    recipe_id = await RecipeService().create_recipe(
        CreatorCreateRecipeRequestSchema(creator_id=request.user_id, **request.dict())
    )
    return await RecipeService().get_recipe_by_id(recipe_id)


@recipe_v1_router.put(
    "/{recipe_id}",
    response_model=GetFullRecipeResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin, ProvidesUserID]]))],
)
@version(1)
async def update_recipe(recipe_id: int, request: UserCreateRecipeRequestSchema):
    await RecipeService().update_recipe(recipe_id, request)
    return await RecipeService().get_recipe_by_id(recipe_id)


@recipe_v1_router.delete(
    "/{recipe_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    status_code=204,
    dependencies=[Depends(PermissionDependency([[IsAdmin, ProvidesUserID]]))],
)
@version(1)
async def delete_recipe(recipe_id: int):
    await RecipeService().delete_recipe(recipe_id)
    return {"message": "Recipe deleted successfully."}
