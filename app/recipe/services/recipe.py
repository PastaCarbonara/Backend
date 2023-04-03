from typing import List
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from app.ingredient.services.ingredient import IngredientService
from app.recipe.schemas import (
    CreatorCreateRecipeRequestSchema,
    GetFullRecipeResponseSchema,
)
from core.db.models import RecipeIngredient, RecipeJudgement, Recipe, RecipeTag, User
from core.db import Transactional, session
from core.exceptions import RecipeNotFoundException, UserNotFoundException


class RecipeService:
    def __init__(self):
        ...

    @Transactional()
    async def judge_recipe(self, recipe_id: int, user_id: int, like: bool) -> None:
        recipe_query = select(Recipe).where(Recipe.id == recipe_id)
        result = await session.execute(recipe_query)
        recipe = result.scalars().first()
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

        db_recipe = Recipe(
            name=recipe.name,
            description=recipe.description,
            image=recipe.image,
            preparing_time=recipe.preparing_time,
            instructions=recipe.instructions,
            creator_id=recipe.creator_id,
        )

        for i in recipe.ingredients:
            db_recipe.ingredients.append(
                RecipeIngredient(unit=i.unit, amount=i.amount, ingredient_id=i.id),
            )

        for tag_id in recipe.tags:
            db_recipe.tags.append(RecipeTag(tag_id=tag_id))
        session.add(db_recipe)
        await session.flush()

        return db_recipe.id

    async def get_recipe_by_id(self, recipe_id) -> Recipe:
        query = (
            select(Recipe)
            .where(Recipe.id == recipe_id)
            .options(
                joinedload(Recipe.tags).joinedload(RecipeTag.tag),
                joinedload(Recipe.creator),
                joinedload(Recipe.judgements),
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_recipe_list(self) -> List[Recipe]:
        query = select(Recipe).options(
            joinedload(Recipe.tags).joinedload(RecipeTag.tag),
            joinedload(Recipe.creator),
            joinedload(Recipe.judgements),
            joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient),
        )
        result = await session.execute(query)
        return result.unique().scalars().all()
