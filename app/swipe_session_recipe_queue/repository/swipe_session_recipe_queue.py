from core.db import session
from core.db.models import SwipeSessionRecipeQueue
from core.repository.base import BaseRepo
from sqlalchemy import select, and_
from sqlalchemy.sql.expression import any_


class SwipeSessionRecipeQueueRepository(BaseRepo):
    def __init__(self):
        super().__init__(SwipeSessionRecipeQueue)

    # async def get(self, limit = config.SWIPE_SESSION_RECIPE_QUEUE, offset = 0):
    #     query = (
    #         select(self.model)
    #         .where()
    #     )
    #     query = query.limit(limit).offset(offset)
    #     result = await session.execute(query)

    async def get_by_id(self, model_id: int) -> SwipeSessionRecipeQueue:
        return await super().get_by_id(model_id)

    async def get_by_id_and_filter_swiped(self, model_id, user_id):
        # query = select(SwipeSessionRecipeQueue).filter(
        #     and_(
        #         SwipeSessionRecipeQueue.swipe_session_id == model_id,
        #         ~any_(
        #             uid == user_id
        #             for uid in SwipeSessionRecipeQueue.queue["users"]
        #         )
        #     )
        # )
        query = select(SwipeSessionRecipeQueue).where(
            SwipeSessionRecipeQueue.swipe_session_id == model_id
        )
        result = await session.execute(query)
        queue = result.scalars().first()
        return queue, [q for q in queue.queue if not any(uid == user_id for uid in q["users"])]

        # [
        #     {
        #         "users": [0, 1],
        #         "recipe_id": 0
        #     },
        #     {
        #         "users": [1],
        #         "recipe_id": 0
        #     }
        # ]
