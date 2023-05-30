from typing import Type
from core.repository.base import BaseRepo
from core.db.models import Swipe
from core.db import session
from sqlalchemy import and_, select


class SwipeRepository(BaseRepo):
    def __init__(self):
        super().__init__(Swipe)

    async def get_swipes_by_session_id_and_recipe_id_and_like(swipe_session_id: int, recipe_id: int, like: bool) -> list[Swipe]:
        query = select(Swipe).where(
            and_(
                Swipe.recipe_id == recipe_id,
                Swipe.swipe_session_id == swipe_session_id,
                Swipe.like == like,
            )
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    async def get_by_creds(recipe_id: int, swipe_session_id: int, user_id: int):
        query = select(Swipe).where(
            and_(
                Swipe.recipe_id == recipe_id,
                Swipe.swipe_session_id == swipe_session_id,
                Swipe.user_id == user_id,
            )
        )
        result = await session.execute(query)
        return result.scalars().first()