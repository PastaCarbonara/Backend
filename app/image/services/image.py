from typing import List
from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile
from core.db.models import File
from core.db import Transactional
from PIL import Image
from azure.core.exceptions import ResourceNotFoundError
from app.image.exception.image import (
    InvalidImageException,
    FileIsNotImageException,
    ImageTooLargeException,
)
from app.image.interface.image import ObjectStorageInterface
from app.image.repository.image import ImageRepository
import sys
from app.image.utils import generate_unique_filename
from app.image.exception.image import (
    AzureImageUploadException,
    AzureImageDeleteException,
    FileNotFoundException,
    AzureImageDeleteNotFoundException,
    ImageDependecyException,
)


class ImageService:
    def __init__(
        self, object_storage: ObjectStorageInterface, image_repository: ImageRepository
    ):
        self.object_storage_interface = object_storage
        self.image_repository = image_repository

    async def get_image_by_name(self, filename) -> File:
        image = await self.image_repository.get_image_by_name(filename)
        return image

    async def get_images(self) -> List[File]:
        images = await self.image_repository.get_images()
        return images

    @Transactional()
    async def upload_images(self, images: List[UploadFile]) -> List[File]:
        new_images: List[File] = []
        for image in images:
            await self.validate_image(image)
        for image in images:
            unique_filename = generate_unique_filename(image.filename)
            try:
                await self.object_storage_interface.upload_image(image, unique_filename)
            except Exception as e:
                raise AzureImageUploadException() from e
            image = await self.image_repository.store_image(unique_filename)
            new_images.append(image)
        return new_images

    @Transactional()
    async def delete_image(self, filename: str) -> None:
        image = await self.image_repository.get_image_by_name(filename)
        if not image:
            raise FileNotFoundException()
        try:
            await self.object_storage_interface.delete_image(filename)
        except ResourceNotFoundError as e:
            raise AzureImageDeleteNotFoundException() from e
        except Exception as e:
            print(e)
            raise AzureImageDeleteException() from e
        try:
            await self.image_repository.delete_image(image)
        except IntegrityError as e:
            raise ImageDependecyException() from e

    async def validate_image(self, file: UploadFile):
        # Check if file is an image
        try:
            img = Image.open(file.file)
            img.verify()
        except Exception as e:
            raise FileIsNotImageException()

        # Check file type
        allowed_types = ["image/jpeg", "image/png"]
        if file.content_type not in allowed_types:
            raise InvalidImageException()

        # Check if file is too large
        max_size = 10 * 1024 * 1024  # 10 MB
        f = await file.read()
        print(sys.getsizeof(f))
        if sys.getsizeof(f) > max_size:
            raise ImageTooLargeException()
        await file.seek(0)
