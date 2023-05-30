"""Recipe service module."""

from typing import List, Dict
from core.db.models import RecipeIngredient, Recipe, RecipeTag, User
from core.db import Transactional
from core.exceptions import RecipeNotFoundException, UserNotFoundException
from core.exceptions.base import UnauthorizedException
from app.ingredient.repository.ingredient import IngredientRepository
from app.tag.repository.tag import TagRepository
from app.tag.schemas import CreateTagSchema
from app.recipe.schemas import CreateRecipeSchema, CreateRecipeIngredientSchema
from app.recipe.repository.recipe import RecipeRepository
from app.image.repository.image import ImageRepository
from app.image.exception.image import FileNotFoundException
from app.user.services.user import UserService


class RecipeService:
    """Recipe service.

    Attributes
    ----------
    ingredient_repository : IngredientRepository
        The ingredient repository.
    tag_repository : TagRepository
        The tag repository.
    image_repository : ImageRepository
        The image repository.
    recipe_repository : RecipeRepository
        The recipe repository.
    user_service : UserService
        The user service.

    Methods
    -------
    get_recipe_list()
        Get a list of recipes.
    get_recipe_by_id(recipe_id)
        Get a recipe by id.
    judge_recipe(recipe_id, user_id, like)
        Like a recipe.
    create_recipe(recipe, user_id)
        Create a recipe.
    """

    def __init__(self):
        self.ingredient_repository = IngredientRepository()
        self.tag_repository = TagRepository()
        self.image_repository = ImageRepository()
        self.recipe_repository = RecipeRepository()
        self.user_service = UserService()

    async def get_paginated_recipe_list(
        self, limit: int, offset: int, user: User = None
    ) -> Dict[str, str]:
        """Get a list of recipes.

        Returns
        -------
        List[Recipe]
            A list of recipes.
        """
        recipes, total_count = await self.recipe_repository.get_recipes(
            limit, offset, user.id if user else None
        )
        return {"total_count": total_count, "recipes": recipes}

    async def get_recipe_by_id(self, recipe_id: int) -> Recipe:
        """Get a recipe by id.

        Parameters
        ----------
        recipe_id : int
            The id of the recipe to get.

        Returns
        -------
        Recipe
            The recipe with the given id.

        Raises
        ------
        RecipeNotFoundException
            If the recipe with the given id does not exist.
        """
        recipe = await self.recipe_repository.get_recipe_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException()
        return recipe

    @Transactional()
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
        recipe = await self.recipe_repository.get_recipe_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException

        try:
            await self.user_service.get_by_id(user_id)
        except UserNotFoundException as exc:
            raise UserNotFoundException() from exc

        await self.recipe_repository.judge_recipe(recipe_id, user_id, like)

        return "Ok"

    @Transactional()
    async def create_recipe(self, recipe: CreateRecipeSchema, user_id: int) -> int:
        """Create a recipe.

        Parameters
        ----------
        recipe : CreatorCreateRecipeRequestSchema
            The recipe to create.

        Returns
        -------
        int
            The id of the created recipe.
        Raises
        ------
        FileNotFoundException
            If the image file does not exist.
        UserNotFoundException
            If the creator does not exist.
        """

        image = await self.image_repository.get_image_by_name(recipe.filename)
        if not image:
            raise FileNotFoundException()
        await self.user_service.get_by_id(user_id)
        db_recipe = await self.create_recipe_object(recipe, user_id)
        await self.set_ingredients_of_recipe(db_recipe, recipe.ingredients)
        await self.set_tags_of_recipe(db_recipe, recipe.tags)

        recipe: Recipe = await self.recipe_repository.create_recipe(db_recipe)

        return recipe.id

    async def create_recipe_object(
        self, recipe: CreateRecipeSchema, user_id: int
    ) -> Recipe:
        """Create a recipe object.

        Parameters
        ----------
        recipe : CreatorCreateRecipeRequestSchema
            The recipe to create.

        Returns
        -------
        Recipe
            The created recipe object.
        """
        return Recipe(
            name=recipe.name,
            filename=recipe.filename,
            description=recipe.description,
            preparation_time=recipe.preparation_time,
            instructions=recipe.instructions,
            materials=recipe.materials,
            creator_id=user_id,
        )

    async def set_ingredients_of_recipe(
        self, recipe: Recipe, ingredients: List[CreateRecipeIngredientSchema]
    ) -> None:
        """Add ingredients to a recipe instance

        Parameters
        ----------
        recipe : Recipe
            The recipe to add the ingredients to.
        ingredients : List[CreateRecipeIngredientSchema]
            A list of ingredients.

        Raises
        ------
        IngredientNotFoundException
            If one of the ingredients does not exist.
        """
        recipe_ingredients = []
        for ingredient in ingredients:
            ingredient_object = await self.ingredient_repository.get_ingredient_by_name(
                ingredient.name
            )
            if not ingredient_object:
                ingredient_object = await self.ingredient_repository.create_ingredient(
                    ingredient.name
                )
            recipe_ingredients.append(
                RecipeIngredient(
                    ingredient=ingredient_object,
                    amount=ingredient.amount,
                    unit=ingredient.unit,
                    recipe=recipe,
                )
            )
            recipe.ingredients = recipe_ingredients

    async def set_tags_of_recipe(
        self, recipe: Recipe, tags: List[CreateTagSchema]
    ) -> None:
        """set tags of a recipe instance

        Parameters
        ----------
        recipe : Recipe
            The recipe to add the tags to.
        tags : List[int]
            A list of tag ids.
        """
        recipe_tags = []
        for tag in tags:
            tag_object = await self.tag_repository.get_tag_by_name(tag.name)
            if not tag_object:
                tag_object = await self.tag_repository.create_tag(
                    tag.name, tag.tag_type
                )
            recipe_tags.append(RecipeTag(tag=tag_object, recipe=recipe))

        recipe.tags = recipe_tags

    @Transactional()
    async def delete_recipe(self, recipe_id: int, user: User):
        recipe = await self.recipe_repository.get_recipe_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException()
        if recipe.creator_id != user.id and not user.is_admin:
            raise UnauthorizedException()
        await self.recipe_repository.delete_recipe(recipe)
        return "Ok"
