"""
The module contains a repository class that defines database operations for ingredients. 
"""

from typing import List
from sqlalchemy import select
from core.db import session
from core.db.models import Ingredient
from core.repository.base import BaseRepo


class IngredientRepository(BaseRepo):
    """Repository for ingredient related database operations"""

    def __init__(self):
        super().__init__(Ingredient)

    async def create_by_name(self, name: str) -> Ingredient:
        """Create a new ingredient in the database

        Parameters:
        ----------
            name (str): Name of the ingredient
        Returns:
        -------
            Ingredient: Newly created ingredient object
        """
        ingredient = Ingredient(name=name)
        session.add(ingredient)
        return ingredient

    async def get(self) -> List[Ingredient]:
        """Get all ingredients from the database

        Returns:
        -------
            List[Ingredient]: List of all ingredients in the database
        """
        query = select(Ingredient)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, model_id: int) -> Ingredient:
        """Get an ingredient by ID from the database

        Parameters:
        ----------
            ingredient_id (int): ID of the ingredient
        Returns:
        -------
            Ingredient: Ingredient object matching the given ID, None if not found
        """
        query = select(Ingredient).where(Ingredient.id == model_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_name(self, ingredient_name: str) -> Ingredient:
        """Get an ingredient by name from the database

        Parameters:
        ----------
            ingredient_name (str): Name of the ingredient
        Returns:
        -------
            Ingredient: Ingredient object matching the given name, None if not found
        """
        query = select(Ingredient).where(Ingredient.name == ingredient_name)
        result = await session.execute(query)
        return result.scalars().first()

    async def update(self, ingredient: Ingredient, name: str) -> Ingredient:
        """Update an ingredient in the database

        Parameters:
        ----------
            ingredient (Ingredient): Ingredient object to be updated
            name (str): New name for the ingredient

        Returns:
        -------
            Ingredient: Updated ingredient object
        """
        ingredient.name = name
        await session.flush()
        return ingredient
