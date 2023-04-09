from core.db import session
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from core.db.models import Recipe, Tag, Ingredient


class RecipeRepository:
    async def get_recipes(self):
        query = select(Recipe).options(
            joinedload(Recipe.tags).joinedload(Tag.recipes),
            joinedload(Recipe.ingredients).joinedload(Ingredient.recipes),
            joinedload(Recipe.judgements),
            joinedload(Recipe.creator),
        )
        result = await session.execute(query)
        return result.scalars().all()
