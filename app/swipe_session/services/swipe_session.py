"""
Class business logic for swipe sessions
"""

from datetime import date, datetime
from typing import List
from sqlalchemy import update

from app.recipe.services.recipe import RecipeService
from app.swipe_session.exceptions.swipe_session import DateTooOldException
from app.swipe_session.repository.swipe_session import SwipeSessionRepository
from app.swipe_session.schemas.swipe_session import (
    CreateSwipeSessionSchema,
    UpdateSwipeSessionSchema,
)
from core.db import Transactional, session
from core.db.enums import SwipeSessionEnum
from core.db.models import Recipe, SwipeSession, User
from core.exceptions.swipe_session import SwipeSessionNotFoundException

from .action_docs import actions


class SwipeSessionService:
    """
    This class represents the service layer for the SwipeSession model.
    It interacts with the SwipeSessionRepository and RecipeService to perform
    CRUD operations on the SwipeSession model.
    """

    def __init__(self) -> None:
        """
        Constructor method for SwipeSessionService class.

        Initializes a new instance of SwipeSessionService and sets up SwipeSessionRepository
        and RecipeService objects.
        """
        self.repo = SwipeSessionRepository()
        self.recipe_serv = RecipeService()

    async def get_swipe_session_list(self) -> List[SwipeSession]:
        """
        This method retrieves all swipe sessions from the repository and gets their associated
        matches.

        Returns:
            A list of SwipeSession objects.
        """
        swipe_sessions = await self.repo.get()

        for swipe_session in swipe_sessions:
            swipe_session.matches = await self.get_matches(swipe_session.id)

        return swipe_sessions

    async def get_swipe_sessions_by_group(self, group_id: int) -> list[SwipeSession]:
        """
        This method retrieves all swipe sessions associated with a particular group from the
        repository and gets their associated matches.

        Args:
            group_id: An integer representing the ID of the group.

        Returns:
            A list of SwipeSession objects.
        """
        swipe_sessions = await self.repo.get_by_group(group_id)

        for swipe_session in swipe_sessions:
            swipe_session.matches = await self.get_matches(swipe_session.id)

        return swipe_sessions

    async def get_swipe_session_by_id(self, swipe_session_id: int) -> SwipeSession:
        """
        This method retrieves a swipe session with a particular ID from the repository and gets
        its associated matches.

        Args:
            swipe_session_id: An integer representing the ID of the swipe session.

        Returns:
            A SwipeSession object.
        """
        swipe_session = await self.repo.get_by_id(swipe_session_id)
        if not swipe_session:
            raise SwipeSessionNotFoundException
        swipe_session.matches = await self.get_matches(swipe_session.id)
        return swipe_session

    def convert_date(self, session_date) -> datetime:
        """
        This method converts a date to a datetime object and sets the time to midnight.

        Args:
            session_date: A date object or None.

        Returns:
            A datetime object.
        """
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if isinstance(session_date, date):
            session_date = datetime.combine(session_date, datetime.min.time())

            session_date = session_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        if not session_date:
            return now

        if session_date < now:
            raise DateTooOldException

        return session_date
        # return max(session_date, now)

    async def update_all_in_group_to_paused(self, group_id) -> None:
        """
        This method updates the status of all swipe sessions in a group to paused.

        Args:
            group_id: An integer representing the ID of the group.
        """
        await self.repo.update_by_group_to_paused(group_id)

    async def get_matches(self, swipe_session_id: int) -> list[Recipe]:
        """
        This method retrieves all matches for a particular swipe session from the repository and
        returns them as a list of Recipe objects.

        Args:
            swipe_session_id: An integer representing the ID of the swipe session.

        Returns:
            A list of Recipe objects.
        """

        recipe_ids = await self.repo.get_matches(swipe_session_id)

        if len(recipe_ids) > 1:
            for _ in range(3):  # Error Log this
                print(f"WARNING! THERE SHOULD ONLY BE 1 MATCH, NOT {recipe_ids}!")

        return [await self.recipe_serv.get_recipe_by_id(id) for id in recipe_ids]

    @Transactional()
    async def update_swipe_session(
        self, request: UpdateSwipeSessionSchema, group_id=None
    ) -> int:
        """
        Update an existing swipe session.

        If another session in the group is active and the updated session is set to
        active, the other active session(s) are paused.

        Args:
            request (UpdateSwipeSessionSchema): The update request data.
            user (User): The user making the update.
            group_id (int, optional): The ID of the group associated with the session.

        Returns:
            int: The ID of the updated swipe session.

        Raises:
            SwipeSessionNotFoundException: If the specified swipe session does not exist.
        """
        swipe_session = await self.get_swipe_session_by_id(request.id)

        if not request.session_date:
            request.session_date = swipe_session.session_date
        else:
            request.session_date = self.convert_date(request.session_date)

        if not swipe_session:
            raise SwipeSessionNotFoundException

        if not request.status:
            request.status = swipe_session.status

        else:
            if request.status == SwipeSessionEnum.IN_PROGRESS and group_id:
                await self.update_all_in_group_to_paused(group_id)

        query = (
            update(SwipeSession)
            .where(SwipeSession.id == request.id)
            .values(**request.dict())
        )
        await session.execute(query)

        return swipe_session.id

    @Transactional()
    async def create_swipe_session(
        self, request: CreateSwipeSessionSchema, user: User, group_id: int = None
    ) -> int:
        """
        Create a new swipe session.
        If another session in the group is active and the new session is set to
        active, the other active session(s) are paused.

        Args:
            request (CreateSwipeSessionSchema): The creation request data.
            user (User): The user creating the session.
            group_id (int): The ID of the group associated with the session.

        Returns:
            int: The ID of the newly created swipe session.

        Raises:
            None
        """
        if not group_id:
            # pylint: disable=broad-exception-raised
            raise Exception("Not implemented :,)")
            # pylint: enable=broad-exception-raised

        db_swipe_session = SwipeSession(
            group_id=group_id, user_id=user.id, **request.dict()
        )

        request.session_date = self.convert_date(request.session_date)

        if request.status == SwipeSessionEnum.IN_PROGRESS and group_id:
            await self.update_all_in_group_to_paused(group_id)

        return await self.repo.create(db_swipe_session)

    async def get_swipe_session_actions(self) -> dict:
        """
        Get the available actions for a swipe session.

        Returns:
            dict: A dictionary containing information about the available actions for a swipe
            session.
        """
        return actions
