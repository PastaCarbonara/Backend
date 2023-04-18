from typing import List
from core.db.models import RecipeIngredient, Recipe, RecipeTag
from core.db import Transactional
from core.exceptions import RecipeNotFoundException, UserNotFoundException
from app.ingredient.services.ingredient import IngredientService
from app.ingredient.repository.ingredient import IngredientRepository
from app.tag.services.tag import TagService
from app.tag.repository.tag import TagRepository
from app.recipe.schemas import CreateRecipeSchema, CreateRecipeIngredientSchema
from app.ingredient.exception.ingredient import IngredientNotFoundException
from app.image.repository.image import ImageRepository
from app.image.exception.image import FileNotFoundException
from app.tag.exception.tag import TagNotFoundException
from app.recipe.repository.recipe import RecipeRepository
from app.user.services.user import UserService


class RecipeService:
    def __init__(self):
        self.ingredient_repository = IngredientRepository()
        self.tag_repository = TagRepository()
        self.image_repository = ImageRepository()
        self.recipe_repository = RecipeRepository()
        self.user_service = UserService()

    async def get_recipe_list(self) -> List[Recipe]:
        """Get a list of recipes.

        Returns
        -------
        List[Recipe]
            A list of recipes.
        """
        return await self.recipe_repository.get_recipes()

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
            await self.user_service.get_user_by_id(user_id)
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
        await self.user_service.get_user_by_id(user_id)
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
            preparing_time=recipe.preparing_time,
            instructions=recipe.instructions,
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

    async def set_tags_of_recipe(self, recipe: Recipe, tags: List[int]) -> None:
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
            tag_object = await self.tag_repository.get_tag_by_name(tag)
            if not tag_object:
                tag_object = await self.tag_repository.create_tag(tag)
            recipe_tags.append(RecipeTag(tag=tag_object, recipe=recipe))

        recipe.tags = recipe_tags

    @Transactional()
    async def update_recipe(self, recipe_id, recipe_data: CreateRecipeSchema) -> int:
        """Update a recipe.

        Parameters
        ----------
        recipe_id : int
            The id of the recipe to update.
        recipe_data : CreatorCreateRecipeRequestSchema
            The data to update the recipe with.

        Returns
        -------
        int
            The id of the updated recipe.
        Raises
        ------
        FileNotFoundException
            If the image file does not exist.
        IngredientNotFoundException
            If one of the ingredients does not exist.
        TagNotFoundException
            If one of the tags does not exist.
        RecipeNotFoundException
            If the recipe with the given id does not exist.
        UserNotFoundException
            If the creator does not exist.
        """
        recipe = await self.get_recipe_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException()

        image = await self.image_repository.get_image_by_name(recipe_data.filename)
        if not image:
            raise FileNotFoundException()

        await self.user_service.get_user_by_id(recipe_data.creator_id)

        self.update_recipe_instance(recipe, recipe_data)

        try:
            await self.set_ingredients_of_recipe(recipe, recipe_data.ingredients)
        except IngredientNotFoundException as exc:
            raise IngredientNotFoundException() from exc

        try:
            await self.set_tags_of_recipe(recipe, recipe_data.tags)
        except TagNotFoundException as exc:
            raise TagNotFoundException() from exc

        await self.recipe_repository.update_recipe(recipe)

        return recipe.id

    async def update_recipe_instance(
        recipe: Recipe, recipe_data: CreateRecipeSchema
    ) -> None:
        """Update a recipe instance.

        Parameters
        ----------
        recipe : Recipe
            The recipe to update.
        recipe_data : CreatorCreateRecipeRequestSchema
            The data to update the recipe with.
        """
        recipe.name = recipe_data.name
        recipe.filename = recipe_data.filename
        recipe.description = recipe_data.description
        recipe.preparing_time = recipe_data.preparing_time
        recipe.instructions = recipe_data.instructions
        recipe.creator_id = recipe_data.creator_id

    @Transactional()
    async def delete_recipe(self, recipe_id: int) -> None:
        """Delete a recipe.

        Parameters
        ----------
        recipe_id : int
            The id of the recipe to delete.

        Raises
        ------
        RecipeNotFoundException
            If the recipe with the given id does not exist.
        """
        recipe = await self.get_recipe_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException()
        await self.recipe_repository.delete_recipe(recipe)
