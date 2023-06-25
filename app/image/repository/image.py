"""
The module contains a repository class that defines database operations for image files. 
It implements CRUD functions for images which are stored in the database. 
"""

from sqlalchemy import select
from core.db.models import File
from core.db import session
from core.repository.base import BaseRepo
from app.image.exceptions.image import DuplicateFileNameException


class ImageRepository(BaseRepo):
    """
    A class that interacts with the database to perform CRUD operations on the 'files' table.
    """

    def __init__(self):
        super().__init__(File)

    async def store(self, filename: str, user_id: int) -> File:
        """
        Store the image file with the given filename in the database.

        Args:
            filename (str): The name of the image file.
            user_id (int): The id of the user who uploaded the image file.

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
        file = File(filename=filename, user_id=user_id)
        session.add(file)
        return file

    async def get(self) -> list[File]:
        """
        Get a list of all the image files stored in the database.

        Returns:
            List[File]: A list of File objects representing the image files.
        """
        query = select(File)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_name(self, filename: str) -> File:
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

    async def delete(self, model: File) -> None:
        """
        Delete the given image file from the database.

        Args:
            file (File): The File object representing the image file to be deleted.

        Returns:
            None
        """
        await session.delete(model)
        await session.flush()
