from typing import List
from sqlalchemy import select
from core.db import session
from core.db.models import Ingredient


class IngredientRepository:
    async def create_ingredient(self, name: str) -> Ingredient:
        ingredient = Ingredient(name=name)
        session.add(ingredient)
        return ingredient

    async def get_ingredients(self) -> List[Ingredient]:
        query = select(Ingredient)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient:
        query = select(Ingredient).where(Ingredient.id == ingredient_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_ingredient_by_name(self, ingredient_name: str) -> Ingredient:
        query = select(Ingredient).where(Ingredient.name == ingredient_name)
        result = await session.execute(query)
        return result.scalars().first()

    async def update_ingredient(self, ingredient: Ingredient, name: str) -> Ingredient:
        ingredient.name = name
        await session.flush()
        return ingredient

    async def delete_ingredient(self, ingredient: Ingredient) -> None:
        print(f"Deleting ingredient {ingredient.name}")
        await session.delete(ingredient)
        await session.flush()
