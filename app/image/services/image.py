"""Image Service for handling image related logic."""

from typing import List
from azure.core.exceptions import ResourceNotFoundError
from tempfile import NamedTemporaryFile
from PIL import Image
from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile
from core.db.models import File
from core.db import Transactional
from app.image.exception.image import (
    InvalidImageException,
    CorruptImageException,
    ImageTooLargeException,
)
from app.image.interface.image import ObjectStorageInterface
from app.image.repository.image import ImageRepository
from app.image.utils import generate_unique_filename
from app.image.exception.image import (
    AzureImageUploadException,
    AzureImageDeleteException,
    FileNotFoundException,
    AzureImageDeleteNotFoundException,
    ImageDependecyException,
)
from core.config import config

ALLOWED_TYPES = ["image/jpeg", "image/png"]


class ImageService:
    """
    A service class for handling images.

    Parameters
    ----------
    object_storage : ObjectStorageInterface
        An instance of an object storage interface.

    Attributes
    ----------
    object_storage_interface : ObjectStorageInterface
        An instance of an object storage interface.
    image_repository : ImageRepository
        An instance of an image repository.

    Methods
    -------
    async def get_images() -> List[File]:
        Get a list of images from the repository.

    async def upload_images(images: List[UploadFile]) -> List[File]:
        Upload a list of images to the object storage and repository.

    async def delete_image(filename: str) -> None:
        Delete an image from the object storage and repository.

    async def validate_image(file: UploadFile):
        Validate the metadata of an image file.

    async def is_image_corrupt(file: UploadFile) -> bool:
        Check if an image file is corrupted.

    async def is_image_to_large(file: UploadFile) -> bool:
        Check if an image file exceeds a maximum file size.
    """

    def __init__(self, object_storage: ObjectStorageInterface):
        self.object_storage_interface = object_storage
        self.image_repository = ImageRepository()

    async def get_image_by_name(self, filename) -> File:
        image = await self.image_repository.get_image_by_name(filename)

        if not image:
            raise FileNotFoundException

        return image

    async def get_images(self) -> List[File]:
        """
        Get a list of images from the repository.

        Returns
        -------
        List[File]
            A list of image files.
        """
        images = await self.image_repository.get_images()
        return images

    @Transactional()
    async def upload_images(self, images: List[UploadFile]) -> List[File]:
        """
        Upload a list of images to the object storage and repository.

        Parameters
        ----------
        images : List[UploadFile]
            A list of image files to upload.

        Returns
        -------
        List[File]
            A list of newly uploaded image files.

        Raises
        ------
        InvalidImageException:
            If the image is not a valid image type.
        CorruptImageException:
            If the image is corrupted.
        ImageTooLargeException:
            If the image exceeds the maximum file size.
        AzureImageUploadException:
            If the image could not be uploaded to the object storage.
        """
        new_images: List[File] = []
        for image in images:
            await self.validate_image(image)
        for image in images:
            unique_filename = generate_unique_filename(image.filename)
            try:
                await self.object_storage_interface.upload_image(image, unique_filename)
            except Exception as exc:
                raise AzureImageUploadException() from exc
            image = await self.image_repository.store_image(unique_filename)
            new_images.append(image)
        return new_images

    @Transactional()
    async def delete_image(self, filename: str) -> None:
        """
        Delete an image from the object storage and repository.

        Parameters
        ----------
        filename : str
            The name of the file to delete.

        Returns
        -------
        None

        Raises
        ------
        FileNotFoundException:
            If the image is not found in the repository.
        ImageDependecyException:
            If the image is used by another entity.
        AzureImageDeleteException:
            If the image could not be deleted from the object storage.
        """

        image = await self.image_repository.get_image_by_name(filename)
        if not image:
            raise FileNotFoundException()
        try:
            await self.image_repository.delete_image(image)
        except IntegrityError as exc:
            raise ImageDependecyException() from exc
        try:
            await self.object_storage_interface.delete_image(filename)
        except ResourceNotFoundError as exc:
            raise AzureImageDeleteNotFoundException() from exc
        except Exception as exc:
            print(exc)
            raise AzureImageDeleteException() from exc

    async def validate_image(self, file: UploadFile):
        """
        Validate image to be stored.

        Parameters
        ----------
        filename : str
            The name of the file to validate.

        Raises
        ------
        InvalidImageException:
            If the image is not a valid image type.
        CorruptImageException:
            If the image is corrupted.
        ImageTooLargeException:
            If the image is too large.
        """

        if file.content_type not in ALLOWED_TYPES:
            print(file)
            print(file.content_type)

            raise InvalidImageException()

        if await self.is_image_corrupt(file):
            raise CorruptImageException()

        if await self.is_image_to_large(file):
            raise ImageTooLargeException()

    async def is_image_corrupt(self, file: UploadFile) -> bool:
        """Checks if image is corrupted.

        Parameters
        ----------
        file : UploadFile
            The file to check.

        Returns
        -------
        bool
            True if the image is corrupted, False otherwise.
        """
        try:
            img = Image.open(file.file)
            img.verify()
        except Exception:
            return True
        return False

    async def is_image_to_large(self, file: UploadFile) -> bool:
        """Checks if image is too large.

        Parameters
        ----------
        file : UploadFile
            The file to check.

        Returns
        -------
        bool
            True if the image is too large, False otherwise.
        """

        real_file_size = 0
        with NamedTemporaryFile(delete=False) as temp:
            for chunk in file.file:
                real_file_size += len(chunk)
                if real_file_size > config.IMAGE_MAX_SIZE:
                    return True
                temp.write(chunk)
        await file.seek(0)
        return False
