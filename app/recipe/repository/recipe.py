""" Recipe repository. """

from typing import List
from sqlalchemy import select, func, and_, or_, not_
from sqlalchemy.orm import joinedload, join
from core.db import session
from core.db.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    RecipeTag,
    RecipeJudgement,
    User,
    UserTag,
)
from core.repository.base import BaseRepo

WANTED_TAG_TYPES = ["Keuken", "Dieet"]
UNWANTED_TAG_TYPES = ["Allergieën"]


class RecipeRepository(BaseRepo):
    """Recipe repository.

    Attributes
    ----------
    session : Session
        The database session.

    Methods
    -------
    get()
        Get a list of recipes.
    get_by_id(recipe_id)
        Get a recipe by id.
    get_by_tags(tags)
        Get a list of recipes by tags.
    get_by_ingredients(ingredients)
        Get a list of recipes by ingredients.
    get_judgment(recipe_id, user_id)
        Get a recipe judgement by recipe id and user id.
    """

    def __init__(self):
        super().__init__(Recipe)

    def get_no_dieet_filter_queries(self, user_id, user_tags):
        print("no dieet")
        query = (
            select(Recipe)
            .join(RecipeTag)
            .join(Tag)
            .join(UserTag, isouter=True)
            .where(
                Recipe.id.not_in(
                    select(Recipe.id)
                    .select_from(
                        join(Recipe, RecipeTag, Recipe.id == RecipeTag.recipe_id)
                        .join(Tag, Tag.id == RecipeTag.tag_id)
                        .join(UserTag, UserTag.tag_id == Tag.id)
                    )
                    .where(UserTag.user_id == user_id, Tag.tag_type == "Allergieën")
                )
            )
            .where((UserTag.user_id.is_(None)) | (UserTag.user_id == user_id))
            .order_by(Recipe.id)
        )
        count_query = (
            select(func.count(Recipe.id))
            .join(RecipeTag)
            .join(Tag)
            .join(UserTag, isouter=True)
            .where(
                Recipe.id.not_in(
                    select(Recipe.id)
                    .select_from(
                        join(Recipe, RecipeTag, Recipe.id == RecipeTag.recipe_id)
                        .join(Tag, Tag.id == RecipeTag.tag_id)
                        .join(UserTag, UserTag.tag_id == Tag.id)
                    )
                    .where(UserTag.user_id == user_id, Tag.tag_type == "Allergieën")
                )
            )
            .where((UserTag.user_id.is_(None)) | (UserTag.user_id == user_id))
        )
        return query, count_query

    def get_vegan_filter_queries(self, user_id, user_tags):
        print("vegan")
        query = (
            select(Recipe)
            .join(RecipeTag)
            .join(Tag)
            .where(
                Recipe.id.not_in(
                    select(Recipe.id)
                    .select_from(
                        join(Recipe, RecipeTag, Recipe.id == RecipeTag.recipe_id)
                        .join(Tag, Tag.id == RecipeTag.tag_id)
                        .join(UserTag, UserTag.tag_id == Tag.id)
                    )
                    .where(UserTag.user_id == user_id, Tag.tag_type == "Allergieën")
                )
            )
            .where(Tag.name == "Vegan")
            .order_by(Recipe.id)
        )
        count_query = (
            select(func.count(Recipe.id))
            .join(RecipeTag)
            .join(Tag)
            .where(
                Recipe.id.not_in(
                    select(Recipe.id)
                    .select_from(
                        join(Recipe, RecipeTag, Recipe.id == RecipeTag.recipe_id)
                        .join(Tag, Tag.id == RecipeTag.tag_id)
                        .join(UserTag, UserTag.tag_id == Tag.id)
                    )
                    .where(UserTag.user_id == user_id, Tag.tag_type == "Allergieën")
                )
            )
            .where(Tag.name == "Vegan")
        )
        return query, count_query

    def get_vegetarian_filter_queries(self, user_id, user_tags):
        print("vegetarian")
        query = (
            select(Recipe)
            .join(RecipeTag)
            .join(Tag)
            .where(
                Recipe.id.not_in(
                    select(Recipe.id)
                    .select_from(
                        join(Recipe, RecipeTag, Recipe.id == RecipeTag.recipe_id)
                        .join(Tag, Tag.id == RecipeTag.tag_id)
                        .join(UserTag, UserTag.tag_id == Tag.id)
                    )
                    .where(UserTag.user_id == user_id, Tag.tag_type == "Allergieën")
                )
            )
            .where((Tag.name == "Vegan") | (Tag.name == "Vegetarisch"))
            .order_by(Recipe.id)
        )
        count_query = (
            select(func.count(Recipe.id))
            .join(RecipeTag)
            .join(Tag)
            .where(
                Recipe.id.not_in(
                    select(Recipe.id)
                    .select_from(
                        join(Recipe, RecipeTag, Recipe.id == RecipeTag.recipe_id)
                        .join(Tag, Tag.id == RecipeTag.tag_id)
                        .join(UserTag, UserTag.tag_id == Tag.id)
                    )
                    .where(UserTag.user_id == user_id, Tag.tag_type == "Allergieën")
                )
            )
            .where((Tag.name == "Vegan") | (Tag.name == "Vegetarisch"))
        )
        return query, count_query

    async def get(self, limit: int, offset: int, user_id: int = None) -> List[Recipe]:
        """Get a list of recipes.

        Returns
        -------
        List[Recipe]
            A list of recipes.
        """
        if user_id:
            user_tags = await self.get_user_tags(user_id)
            if len(user_tags) == 0:
                query = select(Recipe)
                count_query = select(func.count()).select_from(Recipe)
            else:
                # apply filters
                if "Vegan" in [tag.name for tag in user_tags]:
                    ## apply vegan filter
                    query, count_query = self.get_vegan_filter_queries(
                        user_id, user_tags
                    )
                elif "Vegetarisch" in [tag.name for tag in user_tags]:
                    ## apply vegetarian filter
                    query, count_query = self.get_vegetarian_filter_queries(
                        user_id, user_tags
                    )
                else:
                    ## apply no dieet filters
                    query, count_query = self.get_no_dieet_filter_queries(
                        user_id, user_tags
                    )

        else:
            query = select(Recipe)
            count_query = select(func.count()).select_from(Recipe)
        # eager load all relationships
        query = query.options(
            joinedload(Recipe.tags).joinedload(RecipeTag.tag),
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            joinedload(Recipe.creator).joinedload(User.account_auth),
            joinedload(Recipe.creator).joinedload(User.image),
            joinedload(Recipe.judgements),
            joinedload(Recipe.image),
        )
        # apply limit and offset
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        # get count of all recipes in database
        result_count = await session.execute(count_query)
        recipes = result.unique().scalars().all()
        count = result_count.scalar()
        # return recipes and count
        return recipes, count

    async def get_user_tags(self, user_id: int):
        query = select(Tag).join(UserTag).where(UserTag.user_id == user_id)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, model_id) -> Recipe:
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
            .where(Recipe.id == model_id)
            .options(
                joinedload(Recipe.tags).joinedload(RecipeTag.tag),
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
                joinedload(Recipe.creator).joinedload(User.account_auth),
                joinedload(Recipe.creator).joinedload(User.image),
                joinedload(Recipe.judgements),
                joinedload(Recipe.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_tags(self, tags: List[str]) -> List[Recipe]:
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

    async def get_by_ingredients(self, ingredients: List[str]) -> List[Recipe]:
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

    async def get_jugment(self, recipe_id: int, user_id: int) -> RecipeJudgement:
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

    async def judge(self, recipe_id: int, user_id: int, like: bool) -> None:
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
        judgement = await self.get_jugment(recipe_id, user_id)
        if judgement:
            judgement.like = like
        else:
            session.add(
                RecipeJudgement(recipe_id=recipe_id, user_id=user_id, like=like)
            )

    # async def update_recipe(self, recipe: Recipe) -> Recipe:
    #     """Update a recipe.

    #     Parameters
    #     ----------
    #     recipe : Recipe
    #         The recipe to update.

    #     Returns
    #     -------
    #     Recipe
    #         The updated recipe.
    #     """
    #     await session.flush()
    #     return recipe
