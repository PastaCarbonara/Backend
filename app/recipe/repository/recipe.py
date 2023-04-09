from typing import List
from core.db import session
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from core.db.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    RecipeTag,
    RecipeJudgement,
)


class RecipeRepository:
    async def get_recipes(self) -> List[Recipe]:
        """Get a list of recipes.

        Returns
        -------
        List[Recipe]
            A list of recipes.
        """
        query = select(Recipe).options(
            joinedload(Recipe.tags).joinedload(Tag.recipes),
            joinedload(Recipe.ingredients).joinedload(Ingredient.recipes),
            joinedload(Recipe.judgements),
            joinedload(Recipe.creator),
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_recipe_by_id(self, recipe_id) -> Recipe:
        """Get a recipe by id.

        Parameters
        ----------
        recipe_id : int
            The id of the recipe to get.

        Returns
        -------
        Recipe
            The recipe with the given id.
        """
        query = (
            select(Recipe)
            .where(Recipe.id == recipe_id)
            .options(
                joinedload(Recipe.tags).joinedload(RecipeTag.tag),
                joinedload(Recipe.creator),
                joinedload(Recipe.judgements),
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
                joinedload(Recipe.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_recipe_by_tags(self, tags: List[str]) -> List[Recipe]:
        """Get a list of recipes by tags.

        Parameters
        ----------
        tags : List[str]
            A list of tags to filter recipes by.

        Returns
        -------
        List[Recipe]
            A list of recipes filtered by the given tags.
        """
        query = (
            select(Recipe)
            .join(Recipe.tags)
            .filter(Tag.name.in_(tags))
            .options(
                joinedload(Recipe.tags).joinedload(RecipeTag.tag),
                joinedload(Recipe.creator),
                joinedload(Recipe.judgements),
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
                joinedload(Recipe.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_recipe_by_ingredients(self, ingredients: List[str]) -> List[Recipe]:
        """Get a list of recipes by ingredients.

        Parameters
        ----------
        ingredients : List[str]
            A list of ingredients to filter recipes by.

        Returns
        -------
        List[Recipe]
            A list of recipes filtered by the given ingredients.
        """
        query = (
            select(Recipe)
            .join(Recipe.ingredients)
            .filter(Ingredient.name.in_(ingredients))
            .options(
                joinedload(Recipe.tags).joinedload(RecipeTag.tag),
                joinedload(Recipe.creator),
                joinedload(Recipe.judgements),
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
                joinedload(Recipe.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def judge_recipe(self, recipe_id: int, user_id: int, like: bool) -> None:
        """Like a recipe.

        Parameters
        ----------
        recipe_id : int
            The id of the recipe to like.
        user_id : int
            The id of the user who likes the recipe.
        like : bool
            True if the user likes the recipe, False if the user dislikes the recipe.
        """

        judgement = RecipeJudgement(recipe_id=recipe_id, user_id=user_id, like=like)
        await session.add(judgement)
        await session.flush()
