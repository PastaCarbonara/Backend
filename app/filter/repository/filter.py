"""Repository for interacting with the database to perform CRUD operations on the user tags."""

from sqlalchemy import select, delete
from core.db import session
from core.db.models import UserTag, Tag

class FilterRepository:
    """Responsible for interacting with the database to perform CRUD operations on the user tags."""

    async def store_filter(self, user_id: int, user_filter: int):
        """Store a filter for a user."""
        session.add(UserTag(user_id=user_id, tag_id=user_filter))

    async def store_filters(self, user_id, user_filters: list[int]):
        """Store filters for a user."""
        session.add_all([UserTag(user_id=user_id, tag_id=filter) for filter in user_filters])

    async def get_all_filters_user(self, user_id) -> list[Tag]:
        """Get all filters for a user."""
        query = select(Tag).join(UserTag).where(UserTag.user_id == user_id)
        result = await session.execute(query)

        return result.scalars().all()
    
    async def delete_filter_user(self, user_id, tag_id):
        """Delete filter"""
        query = delete(UserTag).where(UserTag.user_id == user_id).where(UserTag.tag_id == tag_id)
        await session.execute(query)
    