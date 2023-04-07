from typing import List
from sqlalchemy import select
from core.db import session
from core.db.models import Tag


class TagRepository:
    async def create_tag(self, name: str) -> int:
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
        """

        db_tag = Tag(name=name)
        session.add(db_tag)
        await session.flush()
        return db_tag.id

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

    async def update_tag(self, tag: Tag, name: str) -> Tag:
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
        await session.flush()

    def delete(self, tag):
        self.db.session.delete(tag)
        self.db.session.commit()
