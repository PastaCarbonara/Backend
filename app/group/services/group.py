"""Group service module"""

from typing import List
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
from app.group.schemas.group import CreateGroupSchema
from app.image.interface.image import ObjectStorageInterface
from app.image.services.image import ImageService
from app.swipe_session.services.swipe_session import SwipeSessionService
from app.user.services.user import UserService
from core.db.models import Group, GroupMember, SwipeSession, User
from core.db import Transactional, session
from core.exceptions.group import GroupNotFoundException


class GroupService:
    def __init__(self):
        self.swipe_session_serv = SwipeSessionService()

    async def is_member(self, group_id: int, user_id: int) -> bool:
        """
        Check if user is a member of a group
        
        Parameters
        ----------
        group_id : int
            The group id
        user_id : int
            The user id
        
        Returns
        -------
        bool
            True if user is a member of the group, False otherwise
        """
        result = await session.execute(
            select(GroupMember).where(
                and_(GroupMember.user_id == user_id, GroupMember.group_id == group_id)
            )
        )
        user = result.scalars().first()
        if not user:
            return False

        return True

    async def is_admin(self, group_id: int, user_id: int) -> bool:
        """
        Check if user is an admin of a group
        
        Parameters
        ----------
        group_id : int
            The group id
        user_id : int
            The user id
        
        Returns
        -------
        bool
            True if user is an admin of the group, False otherwise
        """
        result = await session.execute(
            select(GroupMember).where(
                and_(GroupMember.user_id == user_id, GroupMember.group_id == group_id)
            )
        )
        user = result.scalars().first()
        if not user:
            return False

        return user.is_admin

    async def get_group_list(self) -> List[Group]:
        """
        Get a list of all groups

        Returns
        -------
        List[Group]
            A list of all groups
        """
        query = select(Group).options(
            joinedload(Group.users)
            .joinedload(GroupMember.user)
            .joinedload(User.account_auth),
            joinedload(Group.swipe_sessions)
            .joinedload(SwipeSession.swipes),
            joinedload(Group.image)
        )
        result = await session.execute(query)
        groups: list[Group] = result.unique().scalars().all()
        
        for group in groups:
            for swipe_session in group.swipe_sessions:
                swipe_session.matches = await self.swipe_session_serv.get_matches(swipe_session.id)

        return groups

    async def get_groups_by_user(self, user_id) -> list[Group]:
        """
        Get a list of groups that a user is a member of

        Parameters
        ----------
        user_id : int
            The user id

        Returns
        -------
        list[Group]
            A list of groups that the user is a member of
        """
        query = (
            select(Group)
            .join(Group.users)
            .where(GroupMember.user_id == user_id)
            .options(
                joinedload(Group.users)
                .joinedload(GroupMember.user)
                .joinedload(User.account_auth),
                joinedload(Group.swipe_sessions)
                .joinedload(SwipeSession.swipes),
                joinedload(Group.image)
            )
        )
        result = await session.execute(query)
        groups: list[Group] = result.unique().scalars().all()
        
        for group in groups:
            for swipe_session in group.swipe_sessions:
                swipe_session.matches = await self.swipe_session_serv.get_matches(swipe_session.id)

        return groups

    @Transactional()
    async def create_group(
        self,
        request: CreateGroupSchema,
        user_id: int,
        object_storage: ObjectStorageInterface,
    ) -> int:
        """
        Create a group

        Parameters
        ----------
        request : CreateGroupSchema
            The request body
        user_id : int
            The user id
        object_storage : ObjectStorageInterface
            The object storage interface

        Returns
        -------
        int
            The group id
        """
        # Check if file exists
        await ImageService(object_storage).get_image_by_name(request.filename)

        db_group = Group(**request.dict())

        db_group.users.append(
            GroupMember(
                is_admin=True,
                user_id=user_id,
            )
        )

        session.add(db_group)
        await session.flush()

        return db_group.id

    async def get_group_by_id(self, group_id: int) -> Group:
        """
        Get a group by id

        Parameters
        ----------
        group_id : int
            The group id
        
        Returns
        -------
        Group
            The group
        """
        query = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                joinedload(Group.users)
                .joinedload(GroupMember.user)
                .joinedload(User.account_auth),
                joinedload(Group.swipe_sessions)
                .joinedload(SwipeSession.swipes),
                joinedload(Group.image)
            )
        )
        result = await session.execute(query)
        group: Group = result.unique().scalars().first()

        for swipe_session in group.swipe_sessions:
            swipe_session.matches = await self.swipe_session_serv.get_matches(swipe_session.id)

        return group

    @Transactional()
    async def join_group(self, group_id, user_id) -> None:
        """
        Join a group

        Parameters
        ----------
        group_id : int
            The group id
        user_id : int
            The user id
        """
        group = await self.get_group_by_id(group_id)

        if not group:
            raise GroupNotFoundException

        group.users.append(
            GroupMember(
                is_admin=False,
                user=await UserService().get_user_by_id(user_id),
            )
        )
