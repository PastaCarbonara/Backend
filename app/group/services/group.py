from typing import List
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from app.group.schemas.group import CreateGroupSchema, UserCreateGroupSchema
from app.user.services.user import UserService
from core.db.models import Group, GroupMember, User
from core.db import Transactional, session
from core.exceptions.group import GroupNotFoundException


class GroupService:
    def __init__(self):
        ...

    async def is_member(self, group_id: int, user_id: int) -> bool:
        result = await session.execute(
            select(GroupMember).where(and_(GroupMember.user_id == user_id, GroupMember.group_id == group_id))
        )
        user = result.scalars().first()
        if not user:
            return False
        
        return True

    async def is_admin(self, group_id: int, user_id: int) -> bool:
        result = await session.execute(
            select(GroupMember).where(and_(GroupMember.user_id == user_id, GroupMember.group_id == group_id))
        )
        user = result.scalars().first()
        if not user:
            return False
        
        return user.is_admin

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
                .joinedload(GroupMember.user)
                .joinedload(User.profile)
            )
        )
        result = await session.execute(query)
        return result.unique().scalars().first()
    
    @Transactional()
    async def join_group(self, group_id, user_id) -> None:
        group = await self.get_group_by_id(group_id)

        if not group:
            raise GroupNotFoundException
        
        group.users.append(
            GroupMember(
                is_admin=False,
                user=await UserService().get_user_by_id(user_id),
            )
        )
