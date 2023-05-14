"""Repository for interacting with the database to perform CRUD operations on the user tags."""

from sqlalchemy import select, delete, and_, not_, or_
from sqlalchemy.orm import joinedload
from core.db import session
from core.db.models import UserTag, Tag, User, Recipe, RecipeTag


WANTED_TAG_TYPES = ["Keuken", "Dieet"]
UNWANTED_TAG_TYPES = ["Allergieën"]


class FilterRepository:
    """Responsible for interacting with the database to perform CRUD operations on the user tags."""

    async def store_filter(self, user_id: int, user_filter: int):
        """Store a filter for a user."""
        session.add(UserTag(user_id=user_id, tag_id=user_filter))

    async def store_filters(self, user_id, user_filters: list[int]):
        """Store filters for a user."""
        session.add_all(
            [UserTag(user_id=user_id, tag_id=filter) for filter in user_filters]
        )

    async def get_all_filters_user(self, user_id) -> list[Tag]:
        """Get all filters for a user."""
        query = select(Tag).join(UserTag).where(UserTag.user_id == user_id)
        result = await session.execute(query)

        return result.scalars().all()

    async def delete_filter_user(self, user_id, tag_id):
        """Delete filter"""
        query = (
            delete(UserTag)
            .where(UserTag.user_id == user_id)
            .where(UserTag.tag_id == tag_id)
        )
        await session.execute(query)

    async def get_filtered_recipes_user(self, user_id) -> list[Recipe]:
        """Get all recipes filtered from the user tags for a user."""
        query = (
            select(Recipe)
            .join(RecipeTag)
            .join(Tag)
            .join(UserTag, and_(UserTag.tag_id == Tag.id, UserTag.user_id == user_id))
            .filter(
                and_(
                    UserTag.user_id == user_id,
                    not_(Tag.tag_type.in_(UNWANTED_TAG_TYPES)),
                    or_(*[Tag.tag_type == t for t in WANTED_TAG_TYPES]),
                )
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_filtered_recipes_group(self, group_id) -> list[Recipe]:
        """Get all recipes filtered from the user tags for a group."""
        query = (
            select(Recipe)
            .join(RecipeTag)
            .join(UserTag)
            .join(User)
            .where(User.group_id == group_id)
        )
        result = await session.execute(query)
        return result.scalars().all()
