from datetime import date, datetime
from typing import List
from sqlalchemy import update
from app.recipe.services.recipe import RecipeService
from app.swipe_session.repository.swipe_session import SwipeSessionRepository
from core.db import Transactional, session

from app.swipe_session.schemas.swipe_session import (
    CreateSwipeSessionSchema,
    UpdateSwipeSessionSchema,
)
from core.db.enums import SwipeSessionEnum
from core.db.models import Recipe, SwipeSession, User
from core.exceptions.base import UnauthorizedException
from core.exceptions.swipe_session import SwipeSessionNotFoundException


class SwipeSessionService:
    def __init__(self) -> None:
        self.repo = SwipeSessionRepository()
        self.recipe_serv = RecipeService()

    async def get_swipe_session_list(self) -> List[SwipeSession]:
        sessions = await self.repo.get()

        for session in sessions:
            session.matches = await self.get_matches(session.id)

        return sessions

    async def get_swipe_sessions_by_group(self, group_id: int) -> list[SwipeSession]:
        sessions = await self.repo.get_by_group(group_id)

        for session in sessions:
            session.matches = await self.get_matches(session.id)

        return sessions

    async def get_swipe_session_by_id(self, session_id: int) -> SwipeSession:
        session = await self.repo.get_by_id(session_id)
        session.matches = await self.get_matches(session.id)
        return session

    def convert_date(self, session_date) -> datetime:
        if type(session_date) == date:
            session_date = datetime.combine(session_date, datetime.min.time())
        else:
            if not session_date:
                session_date = datetime.now()

            session_date = session_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        return session_date

    async def update_all_in_group_to_paused(self, group_id) -> None:
        await self.repo.update_by_group_to_paused(group_id)

    async def update_all_outdated_to_cancelled(self) -> None:
        await self.repo.update_all_outdated_to_cancelled()

    async def get_matches(self, session_id: int) -> list[Recipe]:
        """Get all matches in swipe session
        
        Should only return 1, we return multiple just in case.
        """

        recipe_ids = await SwipeSessionRepository().get_matches(session_id)

        if len(recipe_ids) > 1:
            for _ in range(3): # Error Log this
                print(f"WARNING! THERE SHOULD ONLY BE 1 MATCH, NOT {recipe_ids}!")

        return [await self.recipe_serv.get_recipe_by_id(id) for id in recipe_ids]

    @Transactional()
    async def update_swipe_session(
        self, request: UpdateSwipeSessionSchema, user: User, group_id=None
    ) -> int:
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
        self, request: CreateSwipeSessionSchema, user: User, group_id: int
    ) -> int:
        db_swipe_session = SwipeSession(
            group_id=group_id, user_id=user.id, **request.dict()
        )

        request.session_date = self.convert_date(request.session_date)

        if request.status == SwipeSessionEnum.IN_PROGRESS and group_id:
            await self.update_all_in_group_to_paused(group_id)

        return await self.repo.create(db_swipe_session)

    async def get_swipe_session_actions(self) -> dict:
        from .action_docs import actions

        return actions
