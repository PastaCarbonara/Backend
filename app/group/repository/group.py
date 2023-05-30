from core.repository.base import BaseRepo
from core.db.session import session
from core.db.models import (
    Group,
    GroupMember,
)
from sqlalchemy import delete, and_


class GroupRepository(BaseRepo):
    def __init__(self):
        super().__init__(Group)

    async def delete_member(self, group_id, user_id):
        query = delete(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        )

        await session.execute(query)
