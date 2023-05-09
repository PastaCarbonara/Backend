""" Recipe repository. """

from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from core.db import session
from core.db.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    RecipeTag,
    RecipeJudgement,
    User,
)


class RecipeRepository:
    """Recipe repository.

    Attributes
    ----------
    session : Session
        The database session.

    Methods
    -------
    get_recipes()
        Get a list of recipes.
    get_recipe_by_id(recipe_id)
        Get a recipe by id.
    get_recipe_by_tags(tags)
        Get a list of recipes by tags.
    get_recipe_by_ingredients(ingredients)
        Get a list of recipes by ingredients.
    get_recipe_jugment(recipe_id, user_id)
        Get a recipe judgement by recipe id and user id.
    """

    async def get_recipes(self, limit: int, offset: int) -> List[Recipe]:
        """Get a list of recipes.

        Returns
        -------
        List[Recipe]
            A list of recipes.
        """
        query = select(Recipe).options(
            joinedload(Recipe.tags).joinedload(RecipeTag.tag),
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            joinedload(Recipe.creator).joinedload(User.account_auth),
            joinedload(Recipe.judgements),
            joinedload(Recipe.image),
        )
        # apply limit and offset
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        # get count of all recipes in database
        result_count = await session.execute(func.count(Recipe.id))
        # return recipes and count
        return result.unique().scalars().all(), result_count.scalar()

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
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
                joinedload(Recipe.creator).joinedload(User.account_auth),
                joinedload(Recipe.judgements),
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
            .where(Tag.name.in_(tags))
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
            .where(Ingredient.name.in_(ingredients))
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

    async def get_recipe_jugment(self, recipe_id: int, user_id: int) -> RecipeJudgement:
        """Get a recipe judgement.

        Parameters
        ----------
        recipe_id : int
            The id of the recipe to get the judgement for.
        user_id : int
            The id of the user to get the judgement for.

        Returns
        -------
        RecipeJudgement
            The recipe judgement.
        """

        query = select(RecipeJudgement).where(
            (RecipeJudgement.recipe_id == recipe_id)
            & (RecipeJudgement.user_id == user_id)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def create_recipe(self, recipe: Recipe) -> Recipe:
        """Create a recipe.

        Parameters
        ----------
        recipe : Recipe
            The recipe to create.

        Returns
        -------
        Recipe
            The created recipe.
        """
        session.add(recipe)
        await session.flush()
        return recipe

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
        judgement = await self.get_recipe_jugment(recipe_id, user_id)
        if judgement:
            judgement.like = like
        else:
            session.add(
                RecipeJudgement(recipe_id=recipe_id, user_id=user_id, like=like)
            )

    async def update_recipe(self, recipe: Recipe) -> Recipe:
        """Update a recipe.

        Parameters
        ----------
        recipe : Recipe
            The recipe to update.

        Returns
        -------
        Recipe
            The updated recipe.
        """
        await session.flush()
        return recipe

    async def delete_recipe(self, recipe: Recipe) -> None:
        """Delete a recipe.

        Parameters
        ----------
        recipe_id : int
            The id of the recipe to delete.
        """
        session.delete(recipe)
