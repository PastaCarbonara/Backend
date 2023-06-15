"""Image Service for handling image related logic."""

from typing import List
from tempfile import NamedTemporaryFile
from azure.core.exceptions import ResourceNotFoundError
from PIL import Image, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile
from io import BytesIO
from core.db.models import File
from core.db import Transactional
from core.config import config

from app.image.exceptions.image import (
    InvalidImageException,
    CorruptImageException,
    ImageTooLargeException,
    AzureImageUploadException,
    AzureImageDeleteException,
    FileNotFoundException,
    AzureImageDeleteNotFoundException,
    FileDependecyException,
)
from app.image.interface.image import ObjectStorageInterface
from app.image.repository.image import ImageRepository
from app.image.utils import generate_unique_filename

# ratio of the image size to the original size: 2048x1496
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
EXTRA_SMALL_SIZE = (
    "xs",
    20,
)  # de width moet 20px zijn en de height moet de juiste ratio hebben
THUMBNAIL_SIZE = ("thumbnail", 0.125)  # 0.125x oorspronkelijke grootte
SMALL_SIZE = ("sm", 0.25)  # 0.25x oorspronkelijke grootte
MEDIUM_SIZE = ("md", 0.5)  # 0.5x oorspronkelijke grootte
LARGE_SIZE = ("lg", 1)  # 1x oorspronkelijke grootte
SIZES = [EXTRA_SMALL_SIZE, SMALL_SIZE, MEDIUM_SIZE, LARGE_SIZE, THUMBNAIL_SIZE]

url = ""
image = {
    "xs": url,
    "sm": url,  # 128x128
    "md": url,  # 200x200 of 0.5 x oorspronkelijke grootte
    "lg": url,  # 300x300 of 1x oorspronkelijke grootte
    "thumbnail": url,  # 150x200
}


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
    image_repo : ImageRepository
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
        self.image_repo = ImageRepository()

    async def get_image_by_name(self, filename) -> File:
        """
        Retrieves an image by filename from the image repository.

        Args:
            filename (str): The name of the image file to retrieve.

        Returns:
            File: The image file that matches the provided filename.

        Raises:
            FileNotFoundException: If no image is found with the provided filename.
        """
        image = await self.image_repo.get_by_name(filename)

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
        images = await self.image_repo.get()
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
            contents = await image.read()
            original_image = Image.open(BytesIO(contents))
            unique_filename = generate_unique_filename(image.filename)

            for size_name, ratio in SIZES:
                transformed_image = self.transform_image(
                    original_image, size_name, ratio
                )
                output = BytesIO()
                transformed_image.save(output, format="webp", quality=80, method=6)
                output.seek(0)
                unique_filename_with_size = (
                    unique_filename.split(".")[0] + f"-{size_name}.webp"
                )
                try:
                    await self.object_storage_interface.upload_image(
                        output, unique_filename_with_size
                    )
                except Exception as exc:
                    raise AzureImageUploadException() from exc
            image = await self.image_repo.store(unique_filename)
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
        FileDependecyException:
            If the image is used by another entity.
        AzureImageDeleteException:
            If the image could not be deleted from the object storage.
        """

        image = await self.image_repo.get_by_name(filename)
        if not image:
            raise FileNotFoundException()
        try:
            await self.image_repo.delete(image)
        except IntegrityError as exc:
            raise FileDependecyException() from exc
        for size_name, _ in SIZES:
            try:
                await self.object_storage_interface.delete_image(
                    filename.split(".")[0] + f"-{size_name}.webp"
                )
            except ResourceNotFoundError as exc:
                raise AzureImageDeleteNotFoundException() from exc
            except Exception as exc:
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

        except FileNotFoundError:
            return True

        except UnidentifiedImageError:
            return True

        except KeyError:
            return True

        except ValueError:
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

    def transform_image(
        self, image: Image.Image, size_name: str, ratio: float
    ) -> Image.Image:
        """Transforms an image to a given size.

        Parameters
        ----------
        image : Image.Image
            The image to transform.
        size_name : str
            The name of the size to transform to.
        ratio : float
            The ratio to transform the image with.

        Returns
        -------
        Image.Image
            The transformed image.

        """
        if size_name != "xs":
            resized_image = image.resize(
                (
                    int(ratio * image.size[0]),
                    int(ratio * image.size[1]),
                )
            )
        else:
            print("resizing to xs")
            resized_image = image.resize(
                (
                    EXTRA_SMALL_SIZE[1],
                    int(EXTRA_SMALL_SIZE[1] * (image.size[1] / image.size[0])),
                )
            )
        return resized_image.convert("RGB")
