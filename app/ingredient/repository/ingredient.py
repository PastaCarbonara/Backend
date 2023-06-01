"""
The module contains a repository class that defines database operations for ingredients. 
"""

from typing import List
from sqlalchemy import select
from core.db import session
from core.db.models import Ingredient


class IngredientRepository:
    """Repository for ingredient related database operations"""

    async def create_ingredient(self, name: str) -> Ingredient:
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

    async def get_ingredients(self) -> List[Ingredient]:
        """Get all ingredients from the database

        Returns:
        -------
            List[Ingredient]: List of all ingredients in the database
        """
        query = select(Ingredient)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient:
        """Get an ingredient by ID from the database

        Parameters:
        ----------
            ingredient_id (int): ID of the ingredient
        Returns:
        -------
            Ingredient: Ingredient object matching the given ID, None if not found
        """
        query = select(Ingredient).where(Ingredient.id == ingredient_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_ingredient_by_name(self, ingredient_name: str) -> Ingredient:
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

    async def update_ingredient(self, ingredient: Ingredient, name: str) -> Ingredient:
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

    async def delete_ingredient(self, ingredient: Ingredient) -> None:
        """Delete an ingredient from the database

        Parameters:
        ----------
            ingredient (Ingredient): Ingredient object to be deleted

        Returns:
        -------
            None
        """
        await session.delete(ingredient)
        await session.flush()
