from typing import List
from app.user.utils import get_password_hash
from core.db.models import User
from app.user.repository.user import UserRepository
from core.db import Transactional, session
from core.exceptions import (
    DuplicateUsernameException,
    UserNotFoundException,
)


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def get_user_list(self) -> List[User]:
        return await self.user_repository.get_user_list()

    async def get_user_by_id(self, user_id: int) -> User:
        """get a user by id.

        Parameters
        ----------
        user_id : int
            The id of the user to get.

        Returns
        -------
        User
            The user with the given id.

        Raises
        ------
        UserNotFoundException
            If the user with the given id does not exist.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user

    @Transactional()
    async def create_user(self, username: str, password: str) -> None:
        user = await self.user_repository.get_user_by_username(username)
        if user:
            raise DuplicateUsernameException()
        hashed_pwd = get_password_hash(password)
        await self.user_repository.create_user(username, hashed_pwd)

    @Transactional()
    async def set_admin(self, user_id: int, is_admin: bool):
        user = await self.get_user_by_id(user_id)
        await self.user_repository.set_admin(user, is_admin)

    async def is_admin(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        return user.profile.is_admin
