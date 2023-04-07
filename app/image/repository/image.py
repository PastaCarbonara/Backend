from typing import List
from sqlalchemy import select
from core.db.models import File
from core.db import session
from app.image.exception.image import DuplicateFileNameException


class ImageRepository:
    async def store_image(self, filename: str) -> File:
        query = select(File).where(File.filename == filename)
        result = await session.execute(query)
        is_exist = result.scalars().first()
        if is_exist:
            raise DuplicateFileNameException()
        file = File(filename=filename)
        session.add(file)
        return file

    async def get_images(self) -> List[File]:
        query = select(File)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_image_by_name(self, filename: str) -> File:
        query = select(File).where(File.filename == filename)
        result = await session.execute(query)
        return result.scalars().first()

    async def delete_image(self, file: File) -> None:
        await session.delete(file)
        await session.flush()
