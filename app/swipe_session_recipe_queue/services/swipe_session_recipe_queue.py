from app.recipe.services.recipe import RecipeService
from app.swipe_session_recipe_queue.exceptions.swipe_session_recipe_queue import (
    QueueAlreadyExistsException,
)
from app.swipe_session_recipe_queue.repository.swipe_session_recipe_queue import (
    SwipeSessionRecipeQueueRepository,
)
from core.config import config
from core.db.models import SwipeSessionRecipeQueue
from core.db.transactional import Transactional


class SwipeSessionRecipeQueueService:
    def __init__(self) -> None:
        self.repo = SwipeSessionRecipeQueueRepository()
        self.recipe_serv = RecipeService()

    # async def get(self, limit = config.SWIPE_SESSION_RECIPE_QUEUE, offset = 0):
    #     return await self.repo.get(limit, offset)

    @Transactional()
    async def get_and_progress_queue(
        self, swipe_session_id, user_id, limit=config.SWIPE_SESSION_RECIPE_QUEUE
    ):
        swipe_session_recipe_queue = await self.repo.get_by_id(swipe_session_id)
        queue = [
            que
            for que in swipe_session_recipe_queue.queue
            if not any(uid == user_id for uid in que["users"])
        ]

        queue = queue[:limit]
        swipe_session_recipe_queue.queue = [
            obj_q
            for obj_q in swipe_session_recipe_queue.queue
            if not any(obj_q["recipe_id"] == que["recipe_id"] for que in queue)
        ]

        return queue

    @Transactional()
    async def create_queue(self, swipe_session_id):
        if await self.repo.get_by_id(swipe_session_id):
            raise QueueAlreadyExistsException

        recipes = await self.recipe_serv.get()

        queue = [{"users": [], "recipe_id": recipe.id} for recipe in recipes]

        swipe_session_recipe_queue = SwipeSessionRecipeQueue(
            swipe_session_id=swipe_session_id, queue=queue
        )
        await self.repo.create(swipe_session_recipe_queue)
