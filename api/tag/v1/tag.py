"""Tag API v1."""
from typing import List
from fastapi import APIRouter, Depends
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version
from app.tag.schemas import TagSchema, CreateTagSchema
from app.tag.services import TagService
from core.fastapi.dependencies.permission import (
    AllowAll,
    IsAuthenticated,
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
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
    response_model=TagSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def create_tag(request: CreateTagSchema):
    """
    Create a new tag.

    ## Parameters
        - request (CreateTagSchema): The schema representing the new tag.

    ## Returns
        TagSchema: The newly created tag.
    """

    return await TagService().create_tag(request)


@tag_v1_router.put(
    "/{tag_id}",
    response_model=TagSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def update_tag(tag_id: int, request: CreateTagSchema):
    """
    Update a tag.

    ## Parameters
        - tag_id (int): The ID of the tag to update.
        - request (CreateTagSchema): The schema representing the updated tag.

    ## Returns
        TagSchema: The updated tag.
    """

    return await TagService().update_tag(tag_id, request)


@tag_v1_router.delete(
    "/{tag_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    status_code=204,
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
async def delete_tag(tag_id: int):
    """
    Delete a tag.

    ## Parameters
        - tag_id (int): The ID of the tag to delete.
    """
    await TagService().delete_tag(tag_id)
    return {"message": "Tag deleted successfully."}
