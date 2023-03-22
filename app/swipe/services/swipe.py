from sqlalchemy import and_, select
from app.swipe.schemas.swipe import CreateSwipeSchema
from core.db import session
from core.db.models import Swipe
from core.db.transactional import Transactional


class SwipeService:
    @Transactional()
    async def create_swipe(self, request: CreateSwipeSchema) -> int:
        db_swipe = Swipe(**request.dict())

        session.add(db_swipe)
        await session.flush()

        return db_swipe.id
    
    async def get_swipe_by_id(self, swipe_id: int) -> Swipe:
        query = select(Swipe).where(Swipe.id==swipe_id)
        result = await session.execute(query)
        return result.scalars().first()
    
    async def get_swipe_by_creds(self, swipe_session_id: int, user_id: int, recipe_id: int) -> Swipe:
        """Get swipe by SessionID, UserID and RecipeID"""

        query = select(Swipe).where(and_(
            Swipe.recipe_id==recipe_id,
            Swipe.swipe_session_id==swipe_session_id,
            Swipe.user_id==user_id
        ))
        result = await session.execute(query)
        return result.scalars().first()

    async def get_swipe_matches(self, swipe_session_id: int, recipe_id: int) -> list[Swipe]:
        """Get swipes by SessionID and RecipeID"""
        
        query = select(Swipe).where(and_(
            Swipe.recipe_id==recipe_id,
            Swipe.swipe_session_id==swipe_session_id
        ))
        result = await session.execute(query)
        return result.scalars().all()
