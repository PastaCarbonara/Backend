"""
The module contains a repository class that defines database operations for user. 
"""

from typing import List
import uuid
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from core.db.models import AccountAuth, User
from core.db import session
from core.db.transactional import Transactional
from core.repository.base import BaseRepo


class UserRepository(BaseRepo):
    """Repository class for accessing and manipulating User objects in the database."""
    def __init__(self):
        super().__init__(User)

    @Transactional()
    async def create_user(self, display_name: str, ctoken: uuid.UUID) -> None:
        """Create a new user.

        Parameters
        ----------
        display_name : str
            Display name for the user.
        ctoken : uuid.UUID
            Client token for the user.

        Returns
        -------
        None
        """
        user = User(display_name=display_name, client_token=ctoken)
        session.add(user)
        await session.flush()
        return user.id

    @Transactional()
    async def create_account_auth(self, user_id, username, password):
        """Create an account authentication instance for a user.

        Parameters
        ----------
        user_id : int
            User id.
        username : str
            Account username.
        password : str
            Account password.

        Returns
        -------
        None
        """
        user = await self.get_by_id(user_id)
        user.account_auth = AccountAuth(username=username, password=password)

    async def get_by_client_token(self, ctoken: uuid.UUID) -> User:
        """Retrieve a user by client token.

        Parameters
        ----------
        ctoken : uuid.UUID
            Client token for the user.

        Returns
        -------
        User
            User instance.
        """
        query = (
            select(User)
            .where(User.client_token == ctoken)
            .options(
                joinedload(User.account_auth),
                joinedload(User.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_id(self, model_id: int) -> User:
        """Get user by id.

        Parameters
        ----------
        user_id : int
            User id.


        Returns
        -------
        User
            User instance.
        """
        query = (
            select(User)
            .where(User.id == model_id)
            .options(
                joinedload(User.account_auth),
                joinedload(User.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()
    
    # async def update

    async def get_by_display_name(self, display_name: str) -> User:
        """Get user by username.

        Parameters
        ----------
        username : str
            Username.

        Returns
        -------
        User
            User instance.
        """
        query = (
            select(User)
            .join(User.account_auth)
            .where(User.display_name == display_name)
            .options(
                joinedload(User.account_auth),
                joinedload(User.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_user_list(self) -> List[User]:
        """Get user list.

        Returns
        -------
        List[User]
            User list.
        """
        query = (
            select(User)
            .options(
                joinedload(User.account_auth),
                joinedload(User.image),
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    @Transactional()
    async def set_admin(self, user: User, is_admin: bool):
        """Set the admin status of a user.

        Parameters
        ----------
        user : User
            User instance.
        is_admin : bool
            Whether or not the user is an admin.

        Returns
        -------
        None
        """
        user.is_admin = is_admin
