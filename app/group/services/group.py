"""
Class business logic for groups
"""

from typing import List
from app.group.schemas.group import CreateGroupSchema
from app.image.interface.image import ObjectStorageInterface
from app.image.services.image import ImageService
from app.swipe_session.services.swipe_session import SwipeSessionService
from app.user.services.user import UserService
from app.group.repository.group import GroupRepository
from core.db.models import Group, GroupMember
from core.db import Transactional, session
from app.group.exceptions.group import (
    AdminLeavingException,
    GroupNotFoundException,
    GroupJoinConflictException,
    NotInGroupException,
)


class GroupService:
    """
    This class provides business logic for managing groups.

    Methods
    -------
    __init__()
        Initializes the SwipeSessionService instance.
    is_member(group_id: int, user_id: int) -> bool
        Checks if a given user is a member of a given group.
    is_admin(group_id: int, user_id: int) -> bool
        Checks if a given user is an admin of a given group.
    get_group_list() -> List[Group]
        Gets a list of all groups.
    get_groups_by_user(user_id) -> list[Group]
        Gets a list of groups for a given user.
    create_group(request: CreateGroupSchema, user_id: int, object_storage: ObjectStorageInterface)
    -> int
        Creates a new group with the given data and adds the user as an admin.
    get_group_by_id(group_id: int) -> Group
        Gets a group by ID.
    join_group(group_id, user_id) -> None
        Adds a user to a group.
    """

    def __init__(self):
        """
        Initializes the SwipeSessionService instance.
        """
        self.repo = GroupRepository()
        self.user_serv = UserService()
        self.image_serv = ImageService
        self.swipe_session_serv = SwipeSessionService()

    async def attach_matches(self, group: Group):
        for swipe_session in group.swipe_sessions:
            swipe_session.matches = await self.swipe_session_serv.get_matches(
                swipe_session.id
            )
        return group

    async def attach_matches_all(self, groups: list[Group]):
        for group in groups:
            group = await self.attach_matches(group)
        return groups

    async def is_member(self, group_id: int, user_id: int) -> bool:
        """
        Checks if a given user is a member of a given group.

        Parameters
        ----------
        group_id : int
            ID of the group to check.
        user_id : int
            ID of the user to check.

        Returns
        -------
        bool
            True if the user is a member of the group, False otherwise.
        """
        user = await self.repo.get_member_by_ids(group_id, user_id)

        if not user:
            return False

        return True

    async def is_admin(self, group_id: int, user_id: int) -> bool:
        """
        Checks if a given user is an admin of a given group.

        Parameters
        ----------
        group_id : int
            ID of the group to check.
        user_id : int
            ID of the user to check.

        Returns
        -------
        bool
            True if the user is an admin of the group, False otherwise.
        """
        user = await self.repo.get_member_by_ids(group_id, user_id)

        if not user:
            return False

        return user.is_admin

    async def get_group_list(self) -> List[Group]:
        """
        Gets a list of all groups.

        Returns
        -------
        List[Group]
            A list of all groups.
        """
        groups: list[Group] = await self.repo.get()
        groups = await self.attach_matches_all(groups)

        return groups

    async def get_groups_by_user(self, user_id) -> list[Group]:
        """
        Get a list of groups that a user is a member of.

        Args:
            user_id (int): The ID of the user to get groups for.

        Returns:
            list[Group]: A list of Group objects that the user is a member of.
        """
        groups = await self.repo.get_by_user_id(user_id)
        groups = await self.attach_matches_all(groups)

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
        await self.image_serv(object_storage).get_image_by_name(request.filename)

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
        Get a group by its ID.

        Args:
            group_id (int): The ID of the group to retrieve.

        Returns:
            Group: The Group object with the specified ID.
        """
        group = await self.repo.get_by_id(group_id)
        group = await self.attach_matches(group)

        return group

    @Transactional()
    async def join_group(self, group_id, user_id) -> None:
        """
        Add a user to a group.

        Args:
            group_id (int): The ID of the group to join.
            user_id (int): The ID of the user to add to the group.

        Raises:
            GroupNotFoundException: If the specified group does not exist.
            GroupJoinConflictException: If the specified user already in the group.
        """
        group = await self.get_group_by_id(group_id)

        if not group:
            raise GroupNotFoundException

        if await self.is_member(group_id, user_id):
            raise GroupJoinConflictException

        group.users.append(
            GroupMember(
                is_admin=False,
                user=await self.user_serv.get_by_id(user_id),
            )
        )

    @Transactional()
    async def leave_group(self, group_id, user_id) -> None:
        """
        Remove a user from a group.

        Args:
            group_id (int): The ID of the group to leave.
            user_id (int): The ID of the user to remove from the group.

        Raises:
            GroupNotFoundException: If the specified group does not exist.
            NotInGroupException: If the specified user is not in the group.
            AdminLeavingException: If the specified user is the group admin.
        """
        group = await self.get_group_by_id(group_id)

        if not group:
            raise GroupNotFoundException

        if not await self.is_member(group_id, user_id):
            raise NotInGroupException

        if await self.is_admin(group_id, user_id):
            raise AdminLeavingException

        await self.repo.delete_member(group_id, user_id)

    async def delete_group(self, group_id) -> None:
        """Delete's a group by given id.

        Parameters
        ----------
        group_id : int
            The id of the group to delete.
        """
        group = await self.repo.get_by_id(group_id)

        if not group:
            raise GroupNotFoundException

        await self.repo.delete(group)
