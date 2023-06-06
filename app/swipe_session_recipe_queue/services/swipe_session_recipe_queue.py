from app.swipe_session_recipe_queue.repository.swipe_session_recipe_queue import (
    SwipeSessionRecipeQueueRepository,
)
from core.config import config
from core.db.models import SwipeSessionRecipeQueue
from core.db.transactional import Transactional


class SwipeSessionRecipeQueueService:
    def __init__(self) -> None:
        self.repo = SwipeSessionRecipeQueueRepository()

    # async def get(self, limit = config.SWIPE_SESSION_RECIPE_QUEUE, offset = 0):
    #     return await self.repo.get(limit, offset)

    @Transactional()
    async def get_and_progress_queue(
        self, swipe_session_id, user_id, limit=config.SWIPE_SESSION_RECIPE_QUEUE
    ):
        queue_obj, queue = await self.repo.get_by_id_and_filter_swiped(
            swipe_session_id, user_id
        )
        queue_obj: SwipeSessionRecipeQueue

        limit = 1
        queue = queue[:limit]
        queue_obj.queue = [
            obj_q for obj_q in queue_obj.queue
            if not any(obj_q["recipe_id"] == q["recipe_id"] for q in queue)
        ]

    async def create_queue(self, swipe_session_id):
        # swipe_session
        ...
