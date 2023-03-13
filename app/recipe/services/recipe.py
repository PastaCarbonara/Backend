from typing import List
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from core.db.models import RecipeJudgement, Recipe, RecipeTag
from core.db import Transactional, session


class RecipeService:
    def __init__(self):
        ...

    @Transactional()
    async def judge_recipe(self, recipe_id: int, user_id: int, like: bool) -> None:
        exists_query = select(RecipeJudgement).where(
            (RecipeJudgement.recipe_id == recipe_id)
            & (RecipeJudgement.user_id == user_id)
        )
        result = await session.execute(exists_query)
        judgment = result.scalars().first()
        if judgment:
            judgment.like = like
        else:
            session.add(
                RecipeJudgement(recipe_id=recipe_id, user_id=user_id, like=like)
            )

    async def get_recipe_list(self) -> List[Recipe]:
        query = select(Recipe).options(
            joinedload(Recipe.tags).joinedload(RecipeTag.tag)
        )
        result = await session.execute(query)
        return result.unique().scalars().all()
