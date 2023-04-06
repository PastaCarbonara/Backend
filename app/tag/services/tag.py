"""
Module for tag-related operations.

This module defines a TagService class that provides methods for 
performing tag-related operations like creating a new tag,
fetching all tags, or fetching a tag by its ID or name.
"""

from typing import List
from sqlalchemy import select
from app.tag.schemas import CreateTagSchema
from core.db.models import Tag
from core.db import Transactional, session
from core.exceptions.tag import TagAlreadyExistsException


class TagService:
    """
    A service class for tag-related operations.

    Methods
    -------
    get_tags() -> List[Tag]:
        Returns a list of all tags.
    create_tag(request: CreateTagSchema) -> int:
        Creates a new tag with the given data and returns the ID of the new tag.
    get_tag_by_id(tag_id: int) -> Tag:
        Returns the tag with the given ID.
    get_tag_by_name(tag_name: str) -> Tag:
        Returns the tag with the given name.
    """

    async def get_tags(self) -> List[Tag]:
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

    @Transactional()
    async def create_tag(self, request: CreateTagSchema) -> int:
        """
        Creates a new tag with the given data and returns the ID of the new tag.

        Parameters
        ----------
        request : CreateTagSchema
            The data needed to create the tag.

        Returns
        -------
        id : int
            The ID of the new tag.

        Raises
        ------
        TagAlreadyExistsException
            If a tag with the given name already exists.
        """
        tag = await self.get_tag_by_name(request.name)
        if tag:
            raise TagAlreadyExistsException

        db_tag = Tag(**request.dict())

        session.add(db_tag)
        await session.flush()

        return db_tag.id

    async def get_tag_by_id(self, tag_id: int) -> Tag:
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
        query = select(Tag).where(Tag.id == tag_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_tag_by_name(self, tag_name: str) -> Tag:
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
