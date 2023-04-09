from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from core.db.models import RecipeIngredient, RecipeJudgement, Recipe, RecipeTag, User
from core.db import Transactional, session
from core.exceptions import RecipeNotFoundException, UserNotFoundException
from app.ingredient.services.ingredient import IngredientService
from app.tag.services.tag import TagService
from app.recipe.schemas import (
    CreatorCreateRecipeRequestSchema,
)
from app.ingredient.exception.ingredient import IngredientNotFoundException
from app.image.repository.image import ImageRepository
from app.image.exception.image import FileNotFoundException
from app.tag.exception.tag import TagNotFoundException
from app.recipe.repository.recipe import RecipeRepository


class RecipeService:
    def __init__(self):
        self.ingredient_service = IngredientService()
        self.tag_service = TagService()
        self.image_repository = ImageRepository()
        self.recipe_repository = RecipeRepository()

    async def get_recipe_list(self) -> List[Recipe]:
        return await self.recipe_repository.get_recipes()

    async def get_recipe_by_id(self, recipe_id: int) -> Recipe:
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

        user_query = select(User).where(User.id == user_id)
        result = await session.execute(user_query)
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        exists_query = select(RecipeJudgement).where(
            (RecipeJudgement.recipe_id == recipe_id)
            & (RecipeJudgement.user_id == user_id)
        )
        result = await session.execute(exists_query)

        judgment = result.scalars().first()
        if judgment:
            judgment.like = like
        else:
            session.add(
                RecipeJudgement(recipe_id=recipe_id, user_id=user_id, like=like)
            )

    @Transactional()
    async def create_recipe(self, recipe: CreatorCreateRecipeRequestSchema) -> int:
        image = await self.image_repository.get_image_by_name(recipe.filename)
        if not image:
            raise FileNotFoundException()

        db_recipe = Recipe(
            name=recipe.name,
            filename=recipe.filename,
            description=recipe.description,
            preparing_time=recipe.preparing_time,
            instructions=recipe.instructions,
            creator_id=recipe.creator_id,
        )
        for i in recipe.ingredients:
            # check if ingredient exists:
            ingredient = await self.ingredient_service.get_ingredient_by_id(i.id)
            if ingredient:
                db_recipe.ingredients.append(
                    RecipeIngredient(
                        unit=i.unit, amount=i.amount, ingredient=ingredient
                    ),
                )
            else:
                raise IngredientNotFoundException()

        for tag_id in recipe.tags:
            tag = await self.tag_service.get_tag_by_id(tag_id)
            if tag:
                db_recipe.tags.append(RecipeTag(tag=tag))
            else:
                raise TagNotFoundException()
        session.add(db_recipe)
        await session.flush()

        return db_recipe.id

    @Transactional()
    async def update_recipe(
        self, recipe_id: int, recipe: CreatorCreateRecipeRequestSchema
    ) -> None:
        image = await self.image_repository.get_image_by_name(recipe.filename)
        if not image:
            raise FileNotFoundException()

        db_recipe = await self.get_recipe_by_id(recipe_id)
        db_recipe.name = recipe.name
        db_recipe.filename = recipe.filename
        db_recipe.description = recipe.description
        db_recipe.preparing_time = recipe.preparing_time
        db_recipe.instructions = recipe.instructions

        # update ingredients
        for i in recipe.ingredients:
            # check if ingredient exists:
            ingredient = await self.ingredient_service.get_ingredient_by_id(i.id)
            if ingredient:
                db_recipe.ingredients.append(
                    RecipeIngredient(
                        unit=i.unit, amount=i.amount, ingredient=ingredient
                    ),
                )
            else:
                raise IngredientNotFoundException()

        # update tags
        for tag_id in recipe.tags:
            tag = await self.tag_service.get_tag_by_id(tag_id)
            if tag:
                db_recipe.tags.append(RecipeTag(tag=tag))
            else:
                raise TagNotFoundException()

    @Transactional()
    async def delete_recipe(self, recipe_id: int) -> None:
        recipe = await self.get_recipe_by_id(recipe_id)
        session.delete(recipe)
