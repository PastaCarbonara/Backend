from sqlalchemy import and_, select, update
from sqlalchemy.orm import joinedload
from core.db import session
from core.db.enums import SwipeSessionEnum
from core.db.models import SwipeSession
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
            .where(and_(SwipeSession.group_id == group_id, SwipeSession.status == SwipeSessionEnum.IN_PROGRESS))
            .values(status=SwipeSessionEnum.PAUSED)
        )
        await session.execute(query)