"""
The module contains a repository class that defines database operations for image files. 
It implements CRUD functions for images which are stored in the database. 
"""

from typing import List
from sqlalchemy import select
from core.db.models import File
from core.db import session
from app.image.exceptions.image import DuplicateFileNameException
from core.repository.base import BaseRepo


class ImageRepository(BaseRepo):
    """
    A class that interacts with the database to perform CRUD operations on the 'files' table.
    """

    async def store_image(self, filename: str) -> File:
        """
        Store the image file with the given filename in the database.

        Args:
            filename (str): The name of the image file.

        Raises:
            DuplicateFileNameException: If a file with the same filename already exists in the
            database.

        Returns:
            File: The stored file object.
        """
        query = select(File).where(File.filename == filename)
        result = await session.execute(query)
        is_exist = result.scalars().first()
        if is_exist:
            raise DuplicateFileNameException()
        file = File(filename=filename)
        session.add(file)
        return file

    async def get_images(self) -> List[File]:
        """
        Get a list of all the image files stored in the database.

        Returns:
            List[File]: A list of File objects representing the image files.
        """
        query = select(File)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_image_by_name(self, filename: str) -> File:
        """
        Get the File object corresponding to the given filename.

        Args:
            filename (str): The name of the image file.

        Returns:
            File: The File object representing the image file.
        """
        query = select(File).where(File.filename == filename)
        result = await session.execute(query)
        return result.scalars().first()

    async def delete_image(self, file: File) -> None:
        """
        Delete the given image file from the database.

        Args:
            file (File): The File object representing the image file to be deleted.

        Returns:
            None
        """
        await session.delete(file)
        await session.flush()
