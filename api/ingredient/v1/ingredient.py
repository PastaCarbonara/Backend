from typing import List

from fastapi import APIRouter, Depends, Query, Request
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version

from app.ingredient.schemas import (
    CreateIngredientSchema,
    IngredientSchema,
)
from app.ingredient.services import IngredientService
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    ProvidesUserID,
    IsAdmin,
)


ingredient_v1_router = APIRouter()


@ingredient_v1_router.get(
    "",
    response_model=List[IngredientSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll]))],
)
@version(1)
async def get_all_ingredients():
    return await IngredientService().get_ingredients()


@ingredient_v1_router.post(
    "",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
@version(1)
async def create_ingredient(request: CreateIngredientSchema):
    ingredient_id = await IngredientService().create_ingredient(request)
    return await IngredientService().get_ingredient_by_id(ingredient_id)
