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
from app.tag.schemas import CreateTagSchema
from app.tag.exceptions.tag import (
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
        self.tag_repo = TagRepository()

    async def get_tags(self) -> List[Tag]:
        """
        Returns a list of all tags.

        Returns
        -------
        tags : List[Tag]
            A list of all tags.
        """
        return await self.tag_repo.get()

    @Transactional()
    async def create_tag(self, request: CreateTagSchema) -> Tag:
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

        Raises
        ------
        TagAlreadyExistsException
            If a tag with the given name already exists.
        """
        tag = await self.tag_repo.get_by_name(request.name)
        if tag:
            raise TagAlreadyExistsException

        return await self.tag_repo.create_tag(request.name, request.tag_type)

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

        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise TagNotFoundException()
        return tag

    async def get_tag_by_name(self, name: str) -> Tag:
        """
        Returns the tag with the given name.

        Parameters
        ----------
        name : str
            The name of the tag.

        Returns
        -------
        tag : Tag
            The tag with the given name.

        Raises
        ------
        TagNotFoundException
            If no tag with the given name exists.
        """

        tag = await self.tag_repo.get_by_name(name)
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
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise TagNotFoundException
        try:
            tag = await self.tag_repo.update(tag, request.name, request.tag_type)
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
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise TagNotFoundException
        try:
            await self.tag_repo.delete(tag)
        except AssertionError as exc:
            raise TagDependecyException from exc
