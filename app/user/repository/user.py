from typing import List
import uuid
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import joinedload
from core.db.models import AccountAuth, User
from core.db import session
from core.db.transactional import Transactional


class UserRepository:
    @Transactional()
    async def create_user(self, display_name: str, ctoken: uuid.UUID) -> None:
        user = User(display_name=display_name, client_token=ctoken)
        session.add(user)
        await session.flush()
        return user.id

    @Transactional()
    async def create_account_auth(self, user_id, username, password):
        user = await self.get_user_by_id(user_id)
        user.account_auth = AccountAuth(username=username, password=password)

    async def get_user_by_client_token(self, ctoken: uuid.UUID) -> User:
        query = (
            select(User)
            .where(User.client_token == ctoken)
            .options(joinedload(User.account_auth))
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User:
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
            .where(User.id == user_id)
            .options(joinedload(User.account_auth))
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_user_by_display_name(self, display_name: str) -> User:
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
            .options(joinedload(User.account_auth))
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
        query = select(User).options(joinedload(User.account_auth))
        result = await session.execute(query)
        return result.scalars().all()

    @Transactional()
    async def set_admin(self, user: User, is_admin: bool):
        user.is_admin = is_admin
