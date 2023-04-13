from datetime import date, datetime
import json
from typing import List
from fastapi import WebSocket
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from app.group.services.group import GroupService
from app.swipe_session.repository.swipe_session import SwipeSessionRepository
from core.db import Transactional, session

from app.swipe_session.schemas.swipe_session import (
    CreateSwipeSessionSchema,
    UpdateSwipeSessionSchema,
)
from core.db.models import SwipeSession, User
from core.exceptions.base import UnauthorizedException
from core.exceptions.swipe_session import SwipeSessionNotFoundException


class SwipeSessionService:
    def __init__(self) -> None:
        self.repo = SwipeSessionRepository()

    async def get_swipe_session_list(self) -> List[SwipeSession]:
        return await self.repo.get()

    async def get_swipe_session_by_group(self, group_id: int) -> list[SwipeSession]:
        return await self.repo.get_by_group(group_id)

    async def get_swipe_session_by_id(self, session_id: int) -> SwipeSession:
        return await self.repo.get_by_id(session_id)
    
    def convert_date(self, session_date) -> datetime:
        if type(session_date) == date:
            session_date = datetime.combine(
                session_date, datetime.min.time()
            )
        else:
            if not session_date:
                session_date = datetime.now()

            session_date = session_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        return session_date

    @Transactional()
    async def update_swipe_session(
        self, request: UpdateSwipeSessionSchema, user: User
    ) -> int:
        request.session_date = self.convert_date(request.session_date)

        swipe_session = await SwipeSessionService().get_swipe_session_by_id(request.id)

        if not swipe_session:
            raise SwipeSessionNotFoundException

        if not request.status:
            request.status = swipe_session.status

        if not await GroupService().is_admin(swipe_session.group_id, user.id):
            raise UnauthorizedException

        query = (
            update(SwipeSession)
            .where(SwipeSession.id == request.id)
            .values(**request.dict())
        )
        await session.execute(query)

        return swipe_session.id

    @Transactional()
    async def create_swipe_session(
        self, request: CreateSwipeSessionSchema, group_id: int, user: User
    ) -> int:
        db_swipe_session = SwipeSession(
            group_id=group_id, user_id=user.id, **request.dict()
        )

        request.session_date = self.convert_date(request.session_date)

        session.add(db_swipe_session)
        await session.flush()

        return db_swipe_session.id

    async def get_swipe_session_actions(self) -> dict:
        from .action_docs import actions

        return actions
