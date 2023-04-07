from typing import List

from fastapi import APIRouter, Depends
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version

from app.ingredient.schemas import (
    IngredientSchema,
)
from app.tag.schemas import TagSchema, CreateTagSchema
from app.tag.services import TagService
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    IsAdmin,
)


tag_v1_router = APIRouter()


@tag_v1_router.get(
    "",
    response_model=List[TagSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))],
)
@version(1)
async def get_all_tags():
    """
    Retrieve a list of all tags.

    ## Returns
    List[TagSchema]: List of all tags.
    """

    return await TagService().get_tags()


@tag_v1_router.post(
    "",
    response_model=IngredientSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def create_tag(request: CreateTagSchema):
    """
    Create a new tag.

    ## Parameters
    - request (CreateTagSchema): The schema representing the new tag.

    ## Returns
    IngredientSchema: The newly created tag.
    """

    tag_id = await TagService().create_tag(request)
    return await TagService().get_tag_by_id(tag_id)
