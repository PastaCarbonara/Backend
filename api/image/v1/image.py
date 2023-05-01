from typing import List
from fastapi import APIRouter, Depends, UploadFile
from core.exceptions import ExceptionResponseSchema
from core.fastapi.dependencies.permission import IsAuthenticated
from core.fastapi_versioning import version
from core.fastapi.dependencies.object_storage import get_object_storage
from core.fastapi.dependencies import (
    AllowAll,
    PermissionDependency,
    IsAdmin,
)
from app.image.schemas import ImageSchema
from app.image.services import ImageService


image_v1_router = APIRouter()


@image_v1_router.get(
    "",
    response_model=List[ImageSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))],
)
@version(1)
async def get_images(object_storage = Depends(get_object_storage)):
    return await ImageService(object_storage).get_images()


@image_v1_router.get(
    "/{filename}",
    response_model=ImageSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))],
)
@version(1)
async def get_images(filename: str, object_storage = Depends(get_object_storage)):
    return await ImageService(object_storage).get_image_by_name(filename)


@image_v1_router.post(
    "",
    response_model=List[ImageSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def create_image(
    images: list[UploadFile], object_storage = Depends(get_object_storage)
):
    return await ImageService(object_storage).upload_images(images)


@image_v1_router.delete(
    "/{filename}",
    status_code=204,
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def delete_image(filename: str, object_storage = Depends(get_object_storage)):
    return await ImageService(object_storage).delete_image(filename)
