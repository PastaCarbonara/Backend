from typing import List
from fastapi import UploadFile
from core.db.models import File
from PIL import Image
from app.image.exceptions.image import (
    InvalidImageException,
    FileIsNotImageException,
    ImageTooLargeException,
)
from app.image.interfaces.AzureBlobInterface import AzureBlobInterface
from app.image.repository.image import ImageRepository


class ImageService:
    def __init__(
        self, object_storage: AzureBlobInterface, image_repository: ImageRepository
    ):
        self.object_storage_interface = object_storage
        self.image_repository = image_repository

    async def get_images(self) -> List[File]:
        images = await self.image_repository.get_images()
        return images

    async def upload_images(self, images: List[UploadFile]) -> List[File]:
        images: List[File] = []
        for image in images:
            await self.validate_image()
        for image in images:
            filename = await self.object_storage_interface.upload_image(image)
            image = await self.image_repository.store_image(filename)
            images.append(image)
        return images

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
        if file.content_length > max_size:
            raise ImageTooLargeException()
