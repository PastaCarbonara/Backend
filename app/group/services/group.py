from typing import List
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from app.group.schemas.group import CreateGroupSchema, UserCreateGroupSchema
from app.user.services.user import UserService
from core.db.models import Group, GroupMember, User
from core.db import Transactional, session


class GroupService:
    def __init__(self):
        ...

    async def get_group_list(self) -> List[Group]:
        query = select(Group).options(
            joinedload(Group.users)
            .joinedload(GroupMember.user)
            .joinedload(User.profile)
        )
        result = await session.execute(query)
        return result.unique().scalars().all()

    @Transactional()
    async def create_group(self, request: UserCreateGroupSchema) -> int:
        group_schema = CreateGroupSchema(**request.dict())

        db_group = Group(**group_schema.dict())

        db_group.users.append(
            GroupMember(
                is_admin=True,
                user=await UserService().get_user_by_id(request.user_id),
            )
        )

        session.add(db_group)
        await session.flush()

        return db_group.id

    async def get_group_by_id(self, group_id: int) -> Group:
        query = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                joinedload(Group.users)
            #     .joinedload(GroupMember.user)
            #     .joinedload(User.profile)
            )
        )
        result = await session.execute(query)
        return result.unique().scalars().first()