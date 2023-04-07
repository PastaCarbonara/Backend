from typing import List
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from app.ingredient.schemas import CreateIngredientSchema
from app.ingredient.repository.ingredient import IngredientRepository
from core.db.models import Ingredient
from core.db import Transactional, session
from core.exceptions.ingredient import IngredientAlreadyExistsException


class IngredientService:
    def __init__(self):
        self.ingredients_repository = IngredientRepository()

    async def get_ingredients(self) -> list[Ingredient]:
        query = select(Ingredient)
        result = await session.execute(query)
        return result.scalars().all()

    @Transactional()
    async def create_ingredient(self, request: CreateIngredientSchema) -> int:
        name = await self.get_ingredient_by_name(request.name)
        if name:
            raise IngredientAlreadyExistsException

        db_ingredient = Ingredient(**request.dict())

        session.add(db_ingredient)
        await session.flush()

        return db_ingredient.id
