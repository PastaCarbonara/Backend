from typing import List
import uuid
from app.user.exception.user import DuplicateClientTokenException
from app.user.utils import generate_name, get_password_hash
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

    async def get_user_by_display_name(self, display_name) -> User:
        return await self.user_repository.get_user_by_display_name(display_name)

    async def get_user_by_client_token(self, ctoken) -> User:
        return await self.user_repository.get_user_by_client_token(ctoken)

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

    async def create_auth_user(self, username: str, password: str) -> int:
        user = await self.user_repository.get_user_by_display_name(username)
        if user:
            raise DuplicateUsernameException()
        hashed_pwd = get_password_hash(password)

        user_id = await self.user_repository.create_user(username, uuid.uuid4())
        await self.user_repository.create_account_auth(user_id, username, hashed_pwd)
        return user_id

    async def create_user_with_client_token(
        self, ctoken: uuid.UUID, display_name: str = None
    ) -> int:
        if not display_name:
            display_name = generate_name()

        if await self.get_user_by_client_token(ctoken):
            raise DuplicateClientTokenException

        return await self.user_repository.create_user(display_name, ctoken)

    async def set_admin(self, user_id: int, is_admin: bool):
        user = await self.get_user_by_id(user_id)
        await self.user_repository.set_admin(user, is_admin)

    async def is_admin(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        return user.is_admin
