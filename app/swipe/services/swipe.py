"""
Module containing the SwipeService class used for managing swipes.
"""

from sqlalchemy import and_, select
from app.swipe.schemas.swipe import CreateSwipeSchema
from core.db import session
from core.db.models import Swipe
from core.db.transactional import Transactional


class SwipeService:
    """
    A service class to handle swipes for recipes.

    Attributes:
        None

    Methods:
        create_swipe(request: CreateSwipeSchema) -> int:
            Create and store swipe in database.

        get_swipe_by_id(swipe_id: int) -> Swipe:
            Retrieve swipe by ID.

        get_swipe_by_creds(
            swipe_session_id: int,
            user_id: int,
            recipe_id: int
        ) -> Swipe:
            Retrieve swipe by SessionID, UserID and RecipeID.

        get_swipes_by_session_id_and_recipe_id_and_like(
            swipe_session_id: int,
            recipe_id: int,
            like: bool
        ) -> list[Swipe]:
            Retrieve swipes by SessionID, RecipeID and Like.
    """
    @Transactional()
    async def create_swipe(self, request: CreateSwipeSchema) -> int:
        """Create and store swipe in database.

        Args:
            request (CreateSwipeSchema): Request model for creating swipe.

        Returns:
            int: ID of the created swipe.
        """
        db_swipe = Swipe(**request.dict())

        session.add(db_swipe)
        await session.flush()

        return db_swipe.id

    async def get_swipe_by_id(self, swipe_id: int) -> Swipe:
        """Retrieve swipe by ID.

        Args:
            swipe_id (int): ID of the swipe.

        Returns:
            Swipe: Swipe instance that matches the ID.
        """
        query = select(Swipe).where(Swipe.id == swipe_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_swipe_by_creds(
        self, swipe_session_id: int, user_id: int, recipe_id: int
    ) -> Swipe:
        """Retrieve swipe by SessionID, UserID and RecipeID.

        Args:
            swipe_session_id (int): ID of the swipe session.
            user_id (int): ID of the user.
            recipe_id (int): ID of the recipe.

        Returns:
            Swipe: Swipe instance that matches the SessionID, UserID and RecipeID.
        """

        query = select(Swipe).where(
            and_(
                Swipe.recipe_id == recipe_id,
                Swipe.swipe_session_id == swipe_session_id,
                Swipe.user_id == user_id,
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_swipes_by_session_id_and_recipe_id_and_like(
        self, swipe_session_id: int, recipe_id: int, like: bool
    ) -> list[Swipe]:
        """Retrieve swipes by SessionID, RecipeID and Like.

        Args:
            swipe_session_id (int): ID of the swipe session.
            recipe_id (int): ID of the recipe.
            like (bool): True if swipe is a like, False if not.

        Returns:
            list[Swipe]: List of Swipe instances that matches the SessionID, RecipeID and Like.
        """
        query = select(Swipe).where(
            and_(
                Swipe.recipe_id == recipe_id,
                Swipe.swipe_session_id == swipe_session_id,
                Swipe.like == like,
            )
        )
        result = await session.execute(query)
        return result.scalars().all()
