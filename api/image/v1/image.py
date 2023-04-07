from typing import List

from fastapi import APIRouter, Depends, Query, Request, UploadFile
from core.exceptions import ExceptionResponseSchema
from core.fastapi_versioning import version

from app.ingredient.schemas import (
    CreateIngredientSchema,
    IngredientSchema,
)
from app.tag.schema import TagSchema, CreateTagSchema
from app.image.schemas import ImageSchema
from app.ingredient.services import IngredientService
from app.image.services import ImageService
from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    ProvidesUserID,
    IsAdmin,
)
from app.image.interface import AzureBlobInterface
from app.image.repository import ImageRepository


image_v1_router = APIRouter()


@image_v1_router.get(
    "",
    response_model=List[ImageSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[AllowAll]]))],
)
@version(1)
async def get_images():
    return await ImageService(AzureBlobInterface, ImageRepository()).get_images()


@image_v1_router.post(
    "",
    response_model=List[ImageSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def create_image(images: list[UploadFile]):
    return await ImageService(AzureBlobInterface, ImageRepository()).upload_images(
        images
    )


@image_v1_router.delete(
    "/{filename}",
    status_code=204,
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def delete_image(filename: str):
    return await ImageService(AzureBlobInterface, ImageRepository()).delete_image(
        filename
    )
