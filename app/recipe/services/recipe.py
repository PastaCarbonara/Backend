from typing import List
from sqlalchemy import or_, select, and_
from core.db.models import RecipeJudgement, Recipe
from core.db import Transactional, session


class RecipeService:
    def __init__(self):
        ...

    @Transactional()
    async def judge_recipe(self, recipe_id: int, user_id: int, like: bool) -> None:
        session.add(RecipeJudgement(recipe_id, user_id, like))

    async def get_recipe_list(self) -> List[Recipe]:
        query = select(Recipe)
        result = await session.execute(query)
        return result.scalars().all()
