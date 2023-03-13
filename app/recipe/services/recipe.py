from typing import List
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from core.db.models import RecipeJudgement, Recipe, RecipeTag, User
from core.db import Transactional, session
from core.exceptions.recipe import RecipeNotFoundExeption
from core.exceptions.user import UserNotFoundException


class RecipeService:
    def __init__(self):
        ...

    @Transactional()
    async def judge_recipe(self, recipe_id: int, user_id: int, like: bool) -> None:
        recipe_query = select(Recipe).where(Recipe.id == recipe_id)
        result = await session.execute(recipe_query)
        recipe = result.scalars().first()
        if not recipe:
            raise RecipeNotFoundExeption

        user_query = select(User).where(User.id == user_id)
        result = await session.execute(user_query)
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

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
