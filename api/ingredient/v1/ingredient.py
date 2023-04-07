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
    return await IngredientService().get_ingredients()


@ingredient_v1_router.get(
    "/{ingredient_id}",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))],
)
@version(1)
async def get_igrdient_by_id(ingredient_id: int):
    return await IngredientService().get_ingredient_by_id(ingredient_id)


@ingredient_v1_router.post(
    "",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def create_ingredient(request: CreateIngredientSchema):
    return await IngredientService().create_ingredient(request)


@ingredient_v1_router.put(
    "/{ingredient_id}",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def update_ingredient(ingredient_id: int, request: CreateIngredientSchema):
    return await IngredientService().update_ingredient(ingredient_id, request)


@ingredient_v1_router.delete(
    "/{ingredient_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    status_code=204,
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def delete_ingredient(ingredient_id: int):
    return await IngredientService().delete_ingredient(ingredient_id)
