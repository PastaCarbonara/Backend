"""
Module containing the SwipeService class used for managing swipes.
"""

from sqlalchemy import and_, select
from app.swipe.schemas.swipe import CreateSwipeSchema
from app.swipe.repository.swipe import SwipeRepository
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

    def __init__(self) -> None:
        self.repo = SwipeRepository()

    @Transactional()
    async def create_swipe(self, request: CreateSwipeSchema) -> int:
        """Create and store swipe in database.

        Args:
            request (CreateSwipeSchema): Request model for creating swipe.

        Returns:
            int: ID of the created swipe.
        """
        return await self.repo.create(Swipe(**request.dict()))

    async def get_swipe_by_id(self, swipe_id: int) -> Swipe:
        """Retrieve swipe by ID.

        Args:
            swipe_id (int): ID of the swipe.

        Returns:
            Swipe: Swipe instance that matches the ID.
        """
        return await self.repo.get_by_id(swipe_id)

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
        return await self.repo.get_by_creds(recipe_id, swipe_session_id, user_id)

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
        return await self.repo.get_by_session_id_and_recipe_id_and_like(
            swipe_session_id, recipe_id, like
        )
