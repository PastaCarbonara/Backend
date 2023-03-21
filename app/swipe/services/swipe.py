from app.swipe.schemas.swipe import CreateSwipeSchema
from core.db import session
from core.db.models import Swipe
from core.db.transactional import Transactional


class SwipeService:
    @Transactional()
    async def create_swipe(self, request: CreateSwipeSchema):
        db_swipe = Swipe(**request.dict())

        session.add(db_swipe)
        await session.flush()

        return db_swipe.id
