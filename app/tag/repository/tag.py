"""
The module contains a repository class that defines database operations for tags. 
"""

from typing import List
from sqlalchemy import select
from core.db import session
from core.db.models import Tag
from core.repository.base import BaseRepo


class TagRepository(BaseRepo):
    """Repository for tag related database operations"""

    def __init__(self):
        super().__init__(Tag)

    async def create_tag(self, name: str, tag_type: str) -> Tag:
        """
        Creates a new tag with the given data and returns the ID of the new tag.

        Parameters
        ----------
        request : CreateTagSchema
            The data needed to create the tag.

        Returns
        -------
        id : int
            The new tag.
        """

        db_tag = Tag(name=name, tag_type=tag_type)
        session.add(db_tag)
        await session.flush()
        return db_tag

    async def get(self) -> List[Tag]:
        """
        Returns a list of all tags.

        Returns
        -------
        tags : List[Tag]
            A list of all tags.
        """
        query = select(Tag)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, model_id: int) -> Tag:
        """
        Returns the tag with the given ID.

        Parameters
        ----------
        tag_id : int
            The ID of the tag.

        Returns
        -------
        tag : Tag
            The tag with the given ID.
        """
        query = select(Tag).where(Tag.id == model_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_name(self, tag_name: str) -> Tag:
        """
        Returns the tag with the given name.

        Parameters
        ----------
        tag_name : str
            The name of the tag.

        Returns
        -------
        tag : Tag
            The tag with the given name.
        """
        query = select(Tag).where(Tag.name == tag_name)
        result = await session.execute(query)
        return result.scalars().first()

    async def update(self, tag: Tag, name: str, tag_type: str) -> Tag:
        """
        Updates the tag with the given ID with the given data.

        Parameters
        ----------
        tag_id : int
            The ID of the tag to update.
        request : CreateTagSchema
            The data to update the tag with.

        Returns
        -------
        tag : Tag
            The updated tag.
        """
        tag.name = name
        tag.tag_type = tag_type
        await session.flush()
        return tag
