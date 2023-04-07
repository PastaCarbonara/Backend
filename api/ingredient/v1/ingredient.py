"""Ingredient API v1."""

from typing import List
from fastapi import APIRouter, Depends
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    IsAdmin,
)
from app.ingredient.schemas import (
    CreateIngredientSchema,
    IngredientSchema,
)
from app.ingredient.services import IngredientService


ingredient_v1_router = APIRouter()


@ingredient_v1_router.get(
    "",
    response_model=List[IngredientSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))],
)
@version(1)
async def get_all_ingredients():
    """Get all ingredients.

    ## Returns
        List[IngredientSchema]: List of all ingredients.
    """

    return await IngredientService().get_ingredients()


@ingredient_v1_router.get(
    "/{ingredient_id}",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))],
)
@version(1)
async def get_ingredient_by_id(ingredient_id: int):
    """Get an ingredient by id.

    ## Parameters
        - ingredient_id (int): The id of the ingredient to retrieve.

    ## Returns
        IngredientSchema: The ingredient with the given id.
    """
    return await IngredientService().get_ingredient_by_id(ingredient_id)


@ingredient_v1_router.post(
    "",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def create_ingredient(request: CreateIngredientSchema):
    """Create a new ingredient.
    ## Parameters
        - request (CreateIngredientSchema): The schema representing the new ingredient.

    ## Returns
        IngredientSchema: The newly created ingredient.
    """

    return await IngredientService().create_ingredient(request)


@ingredient_v1_router.put(
    "/{ingredient_id}",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def update_ingredient(ingredient_id: int, request: CreateIngredientSchema):
    """Update an existing ingredient.
    ## Parameters
        - ingredient_id (int): The id of the ingredient to update.
        - request (CreateIngredientSchema): The schema representing the updated ingredient.

    ## Returns
        IngredientSchema: The updated ingredient.
    """

    return await IngredientService().update_ingredient(ingredient_id, request)


@ingredient_v1_router.delete(
    "/{ingredient_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    status_code=204,
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def delete_ingredient(ingredient_id: int):
    """Delete an existing ingredient.
    ## Parameters
        - ingredient_id (int): The id of the ingredient to delete.

    ## Returns
        None
    """
    return await IngredientService().delete_ingredient(ingredient_id)
