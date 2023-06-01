"""Repository for interacting with the database to perform CRUD operations on the user tags."""

from sqlalchemy import select, delete
from core.db import session
from core.db.models import UserTag, Tag
from core.repository.base import BaseRepo


class FilterRepository(BaseRepo):
    """Responsible for interacting with the database to perform CRUD operations on the user tags."""

    def __init__(self):
        super().__init__(UserTag)

    async def store(self, user_id: int, user_filter: int):
        """Store a filter for a user."""
        session.add(UserTag(user_id=user_id, tag_id=user_filter))

    async def store_all(self, user_id, user_filters: list[int]):
        """Store filters for a user."""
        session.add_all(
            [UserTag(user_id=user_id, tag_id=filter) for filter in user_filters]
        )

    async def get_by_user_id(self, user_id) -> list[Tag]:
        """Get all filters for a user."""
        query = select(Tag).join(UserTag).where(UserTag.user_id == user_id)
        result = await session.execute(query)

        return result.scalars().all()

    async def delete_by_ids(self, user_id, tag_id):
        """Delete filter"""
        query = (
            delete(UserTag)
            .where(UserTag.user_id == user_id)
            .where(UserTag.tag_id == tag_id)
        )
        await session.execute(query)
