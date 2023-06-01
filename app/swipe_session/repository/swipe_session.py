"""
Class containing crud logic for swipe session
"""

from sqlalchemy import and_, distinct, func, join, select, update
from sqlalchemy.orm import joinedload
from core.db import session
from core.db.enums import SwipeSessionEnum
from core.db.models import (
    GroupMember,
    Swipe,
    SwipeSession,
    Group,
)
from core.repository.base import BaseRepo


class SwipeSessionRepository(BaseRepo):
    """Repository class for `SwipeSession` model.

    This class provides methods to interact with the `SwipeSession` model in the database.

    Args:
        BaseRepo (class): The base repository class from which this class inherits.

    Attributes:
        model (class): The `SwipeSession` model class.

    """
    def __init__(self):
        super().__init__(SwipeSession)

    async def get(self):
        """Retrieve all swipe sessions with their swipes.

        Returns:
            list[SwipeSession]: List of `SwipeSession` instances with their `swipes`.
        """
        query = select(self.model).options(joinedload(self.model.swipes))

        result = await session.execute(query)
        return result.unique().scalars().all()

    async def get_by_group(self, group_id) -> list[SwipeSession]:
        """Retrieve all swipe sessions for a group.

        Args:
            group_id (int): ID of the group.

        Returns:
            list[SwipeSession]: List of `SwipeSession` instances for the group with their `swipes`.
        """
        query = (
            select(self.model)
            .where(self.model.group_id == group_id)
            .options(
                joinedload(self.model.swipes),
            )
        )
        result = await session.execute(query)
        return result.scalars().unique().all()

    async def get_by_id(self, model_id: int) -> SwipeSession:
        """Retrieve a swipe session by ID.

        Args:
            id (int): ID of the swipe session.

        Returns:
            SwipeSession: The `SwipeSession` instance with the specified ID.
        """
        query = (
            select(self.model)
            .where(self.model.id == model_id)
            .options(
                joinedload(self.model.swipes),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def update_by_group_to_paused(self, group_id: int) -> None:
        """Update swipe sessions for a group to `PAUSED` status.

        Args:
            group_id (int): ID of the group.
        """
        query = (
            update(self.model)
            .where(
                and_(
                    SwipeSession.group_id == group_id,
                    SwipeSession.status == SwipeSessionEnum.IN_PROGRESS,
                )
            )
            .values(status=SwipeSessionEnum.PAUSED)
        )
        await session.execute(query)

    async def get_matches(self, session_id: int) -> int:
        """Retrieve recipe IDs that have a match for a swipe session.

        Args:
            session_id (int): ID of the swipe session.

        Returns:
            int: List of recipe IDs that have a match for the swipe session.
        """
        group_size = (
            select(func.count(distinct(GroupMember.user_id))) # pylint: disable=not-callable
            .where(GroupMember.group_id == Group.id)
            .where(SwipeSession.id == session_id)
            .select_from(join(GroupMember, Group).join(SwipeSession))
            .scalar_subquery()
        )
        query = (
            select(Swipe.recipe_id)
            .join(SwipeSession, Swipe.swipe_session_id == SwipeSession.id)
            .join(Group, Group.id == SwipeSession.group_id)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(
                and_(
                    SwipeSession.id == session_id,
                    Swipe.like is True,
                )
            )
            .group_by(Swipe.recipe_id)
            .having(
                func.count(distinct(Swipe.user_id)) == group_size # noqa pylint: disable=not-callable
            )
        )
        result = await session.execute(query)
        return result.scalars().all()
