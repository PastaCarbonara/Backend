from typing import List
from sqlalchemy.exc import IntegrityError
from app.ingredient.schemas import CreateIngredientSchema
from app.ingredient.repository.ingredient import IngredientRepository
from app.ingredient.exception.ingredient import (
    IngredientAlreadyExistsException,
    IngredientNotFoundException,
    IngredientDependecyException,
)
from core.db.models import Ingredient
from core.db import Transactional


class IngredientService:
    def __init__(self):
        self.ingredient_repository = IngredientRepository()

    async def get_ingredients(self) -> list[Ingredient]:
        return await self.ingredient_repository.get_ingredients()

    async def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient:
        ingredient = await self.ingredient_repository.get_ingredient_by_id(
            ingredient_id
        )
        if not ingredient:
            raise IngredientNotFoundException
        return await self.ingredient_repository.get_ingredient_by_id(ingredient_id)

    @Transactional()
    async def create_ingredient(self, request: CreateIngredientSchema) -> Ingredient:
        ingredient = await self.ingredient_repository.get_ingredient_by_name(
            request.name
        )
        if ingredient:
            raise IngredientAlreadyExistsException

        return await self.ingredient_repository.create_ingredient(request.name)

    @Transactional()
    async def update_ingredient(
        self, ingredient_id: int, request: CreateIngredientSchema
    ) -> Ingredient:
        ingredient = await self.ingredient_repository.get_ingredient_by_id(
            ingredient_id
        )
        if not ingredient:
            raise IngredientNotFoundException
        try:
            return await self.ingredient_repository.update_ingredient(
                ingredient, request.name
            )
        except IntegrityError as exc:
            raise IngredientAlreadyExistsException from exc

    @Transactional()
    async def delete_ingredient(self, ingredient_id: int) -> None:
        ingredient = await self.ingredient_repository.get_ingredient_by_id(
            ingredient_id
        )
        if not ingredient:
            raise IngredientNotFoundException

        try:
            await self.ingredient_repository.delete_ingredient(ingredient)
        except AssertionError as exc:
            raise IngredientDependecyException from exc
