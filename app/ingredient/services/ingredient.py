"""This module contains the `IngredientService` class that provides ingredients 
    related operations"""
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
    """
    A service class that provides ingredient related operations.

    Attributes
    ----------
    ingredient_repository : `IngredientRepository`
        An instance of `IngredientRepository` that provides access to the
        ingredient data.

    Methods
    -------
    get_ingredients() -> list[Ingredient]:
        Returns a list of all the ingredients.

    get_ingredient_by_id(ingredient_id: int) -> Ingredient:
        Returns an ingredient with a given ID.

    create_ingredient(request: CreateIngredientSchema) -> Ingredient:
        Creates a new ingredient.

    update_ingredient(ingredient_id: int, request: CreateIngredientSchema) -> Ingredient:
        Updates an ingredient with a given ID.

    delete_ingredient(ingredient_id: int) -> None:
        Deletes an ingredient with a given ID.
    """

    def __init__(self):
        """initializes the service"""
        self.ingredient_repository = IngredientRepository()

    async def get_ingredients(self) -> List[Ingredient]:
        """
        Returns a list of all the ingredients.

        Parameters
        ----------
        None

        Returns
        -------
        list[Ingredient]
            A list of all the ingredients.
        """
        return await self.ingredient_repository.get_ingredients()

    async def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient:
        """
        Returns an ingredient with a given ID.

        Parameters
        ----------
        ingredient_id : int
            The ID of the ingredient to retrieve.

        Returns
        -------
        Ingredient
            An instance of the `Ingredient` model class with the given ID.

        Raises
        ------
        IngredientNotFoundException
            If no ingredient with the given ID exists.
        """
        ingredient = await self.ingredient_repository.get_ingredient_by_id(
            ingredient_id
        )
        if not ingredient:
            raise IngredientNotFoundException
        return await self.ingredient_repository.get_ingredient_by_id(ingredient_id)

    async def get_ingredient_by_name(self, ingredient_name: str) -> Ingredient:
        """
        Returns an ingredient with a given name.

        Parameters
        ----------
        ingredient_name : str
            The name of the ingredient to retrieve.

        Returns
        -------
        Ingredient
            An instance of the `Ingredient` model class with the given name.

        Raises
        ------
        IngredientNotFoundException
            If no ingredient with the given name exists.
        """
        ingredient = await self.ingredient_repository.get_ingredient_by_name(
            ingredient_name
        )
        if not ingredient:
            raise IngredientNotFoundException
        return ingredient

    @Transactional()
    async def create_ingredient(self, request: CreateIngredientSchema) -> Ingredient:
        """
        Creates a new ingredient.

        Parameters
        ----------
        request : `CreateIngredientSchema`
            An instance of the `CreateIngredientSchema` class that represents
            the new ingredient to create.

        Returns
        -------
        Ingredient
            An instance of the `Ingredient` model class that represents the
            newly created ingredient.

        Raises
        ------
        IngredientAlreadyExistsException
            If an ingredient with the same name already exists.
        """
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
        """
        Updates an ingredient with a given ID.

        Parameters
        ----------
        ingredient_id : int
            The ID of the ingredient to update.
        request : `CreateIngredientSchema`
            An instance of the `CreateIngredientSchema` class that represents
            the updated ingredient.

        Returns
        -------
        Ingredient
            An instance of the `Ingredient` model class that represents the
            updated ingredient.

        Raises
        ------
        IngredientNotFoundException
            If no ingredient with the given ID exists.
        IngredientAlreadyExistsException
            If an ingredient with the same name already exists.
        """
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
        """
        Delete an ingredient by ID.

        Parameters
        ----------
        ingredient_id : int
            The ID of the ingredient to be deleted.

        Raises
        ------
        IngredientNotFoundException
            If no ingredient with the given ID is found.
        IngredientDependecyException
            If the ingredient cannot be deleted because it is a dependency of another entity.

        Returns
        -------
        None
        """
        ingredient = await self.ingredient_repository.get_ingredient_by_id(
            ingredient_id
        )
        if not ingredient:
            raise IngredientNotFoundException

        try:
            await self.ingredient_repository.delete_ingredient(ingredient)
        except AssertionError as exc:
            raise IngredientDependecyException from exc
