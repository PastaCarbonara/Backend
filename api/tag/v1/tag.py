from typing import List

from fastapi import APIRouter, Depends, Query, Request
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version

from app.ingredient.schemas import (
    CreateIngredientSchema,
    IngredientSchema,
)
from app.tag.schemas import TagSchema, CreateTagSchema
from app.ingredient.services import IngredientService
from app.tag.services import TagService
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    ProvidesUserID,
    IsAdmin,
)


tag_v1_router = APIRouter()


@tag_v1_router.get(
    "",
    response_model=List[TagSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([AllowAll]))],
)
@version(1)
async def get_all_tags():
    return await TagService().get_tags()


@tag_v1_router.post(
    "",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
@version(1)
async def create_tag(request: CreateTagSchema):
    tag_id = await TagService().create_tag(request)
    return await TagService().get_tag_by_id(tag_id)
