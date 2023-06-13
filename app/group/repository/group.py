from core.repository.base import BaseRepo
from core.db.session import session
from core.db.models import (
    Group,
    GroupMember,
    Recipe,
    User,
    SwipeSession,
)
from sqlalchemy import delete, and_, select
from sqlalchemy.orm import joinedload


class GroupRepository(BaseRepo):
    def __init__(self):
        super().__init__(Group)

    def query_options(self, query):
        return query.options(
            joinedload(Group.users).joinedload(GroupMember.user).joinedload(User.account_auth),
            joinedload(Group.users).joinedload(GroupMember.user).joinedload(User.image),
            joinedload(Group.swipe_sessions).joinedload(SwipeSession.swipes),
            joinedload(Group.swipe_sessions).joinedload(SwipeSession.swipe_match).joinedload(Recipe.image),
            joinedload(Group.image),
        )

    async def get(self) -> list[Group]:
        query = select(Group)
        query = self.query_options(query)
        result = await session.execute(query)
        return result.unique().scalars().all()

    async def get_by_user_id(self, user_id) -> list[Group]:
        query = (
            select(Group)
            .join(Group.users)
            .where(GroupMember.user_id == user_id)
        )
        query = self.query_options(query)
        result = await session.execute(query)
        return result.unique().scalars().all()

    async def get_member(self, user_id, group_id) -> GroupMember:
        result = await session.execute(
            select(GroupMember).where(
                and_(GroupMember.user_id == user_id, GroupMember.group_id == group_id)
            )
        )
        return result.scalars().first()

    async def delete_member(self, group_id, user_id) -> None:
        query = delete(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        )

        await session.execute(query)

    async def get_member_by_ids(self, group_id, user_id):
        query = select(GroupMember).where(
            and_(GroupMember.user_id == user_id, GroupMember.group_id == group_id)
        )
        result = await session.execute(query)
        return result.scalars().first()
