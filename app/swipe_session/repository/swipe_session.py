from sqlalchemy import and_, case, desc, distinct, func, join, literal, select, update
from sqlalchemy.orm import joinedload, aliased
from core.db import session
from core.db.enums import SwipeSessionEnum
from core.db.models import (
    GroupMember,
    Recipe,
    RecipeIngredient,
    Swipe,
    SwipeSession,
    Group,
)
from core.repository.base import BaseRepo


class SwipeSessionRepository(BaseRepo):
    def __init__(self):
        super().__init__(SwipeSession)

    async def get(self):
        query = select(self.model).options(joinedload(self.model.swipes))

        result = await session.execute(query)
        return result.unique().scalars().all()

    async def get_by_group(self, group_id) -> list[SwipeSession]:
        query = (
            select(self.model)
            .where(self.model.group_id == group_id)
            .options(
                joinedload(self.model.swipes),
            )
        )
        result = await session.execute(query)
        return result.scalars().unique().all()

    async def get_by_id(self, id: int) -> SwipeSession:
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                joinedload(self.model.swipes),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def update_by_group_to_paused(self, group_id: int) -> None:
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
        group_size = (
            select(func.count(distinct(GroupMember.user_id)))
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
                    Swipe.like == True,
                )
            )
            .group_by(Swipe.recipe_id)
            .having(
                func.count(distinct(Swipe.user_id)) == group_size
            )
        )
        result = await session.execute(query)
        return result.scalars().all()
