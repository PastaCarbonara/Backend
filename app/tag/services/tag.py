"""
Module for tag-related operations.

This module defines a TagService class that provides methods for 
performing tag-related operations like creating a new tag,
fetching all tags, or fetching a tag by its ID or name.
"""

from typing import List
from sqlalchemy.exc import IntegrityError
from core.db.models import Tag
from core.db import Transactional
from app.tag.schema import CreateTagSchema
from app.tag.exception.tag import (
    TagAlreadyExistsException,
    TagNotFoundException,
    TagDependecyException,
)
from app.tag.repository.tag import TagRepository


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

    def __init__(self):
        self.tag_repository = TagRepository()

    async def get_tags(self) -> List[Tag]:
        """
        Returns a list of all tags.

        Returns
        -------
        tags : List[Tag]
            A list of all tags.
        """
        return await self.tag_repository.get_tags()

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
        tag = await self.tag_repository.get_tag_by_name(request.name)
        if tag:
            raise TagAlreadyExistsException

        return await self.tag_repository.create_tag(request.name)

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

        Raises
        ------
        TagNotFoundException
            If no tag with the given ID exists.
        """

        tag = await self.tag_repository.get_tag_by_id(tag_id)
        if not tag:
            raise TagNotFoundException()
        return tag

    @Transactional()
    async def update_tag(self, tag_id: int, request: CreateTagSchema) -> Tag:
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
        tag = await self.tag_repository.get_tag_by_id(tag_id)
        if not tag:
            raise TagNotFoundException
        try:
            tag = await self.tag_repository.update_tag(tag, request.name)
        except IntegrityError as exc:
            raise TagAlreadyExistsException from exc
        return tag

    @Transactional()
    async def delete_tag(self, tag_id: int) -> None:
        """
        Deletes the tag with the given ID.

        Parameters
        ----------
        tag_id : int
            The ID of the tag to delete.

        Raises
        ------
        TagNotFoundException
            If no tag with the given ID exists.
        """
        tag = await self.tag_repository.get_tag_by_id(tag_id)
        if not tag:
            raise TagNotFoundException
        try:
            await self.tag_repository.delete_tag(tag)
        except AssertionError as exc:
            raise TagDependecyException from exc
