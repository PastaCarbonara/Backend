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

    async def get_match(self, session_id) -> int:
        # swipes_query = (
        #     select(Swipe).where(Swipe.swipe_session_id == session_id)
        # )
        # swipes = await session.execute(swipes_query)
        # swipes = swipes.scalars().all()

        # swipes_dict = {}
        # for swipe in swipes:
        #     if not swipe.like: continue
        #     x = swipe.recipe_id

        #     if not swipes_dict.get(x):
        #         swipes_dict[x] = 1
        #     else: swipes_dict[x] += 1

        # swipe_session_query = (
        #     select(SwipeSession.group_id).where(SwipeSession.id == session_id)
        # )
        # swipe_session = await session.execute(swipe_session_query)
        # swipe_session = swipe_session.scalars().first()

        # group_query = (
        #     select(Group).where(Group.id == swipe_session)
        #     .options(joinedload(Group.users))
        # )
        # group = await session.execute(group_query)
        # group = group.scalars().first()

        # user_count = len(group.users)
        # for i in swipes_dict.keys():
        #     if swipes_dict[i] == user_count:
        #         return i
        # return None
        query = (
            select(Swipe.recipe_id)
            .join(SwipeSession, Swipe.swipe_session_id == SwipeSession.id)
            .join(Group, Group.id == SwipeSession.group_id)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(and_(SwipeSession.id == 1,
                        GroupMember.group_id == 1,
                        Swipe.like == True))
            .group_by(Swipe.recipe_id)
            .having(func.count(distinct(Swipe.user_id)) == select(func.count(distinct(GroupMember.user_id))).where(GroupMember.group_id == 2).scalar_subquery())
        )
        result = await session.execute(query)
        return result.scalars().all()
