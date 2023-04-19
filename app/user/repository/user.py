from typing import List
import uuid
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import joinedload
from core.db.models import User
from core.db import session


class UserRepository:
    async def create_user(self, username: str, ctoken: uuid.UUID) -> None:
        user = User()
        session.add(user)
        await session.flush()

        user_profile = User(
            display_name=username, client_token=ctoken
        )
        session.add(user_profile)

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
        query = select(User).where(User.id == user_id).options(joinedload(User.profile))
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
            .join(User.profile)
            .where(User.display_name == display_name)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_user_list(self) -> List[User]:
        """Get user list.

        Returns
        -------
        List[UserProfile]
            User list.
        """
        query = select(User)#.options(joinedload(User.profile))
        result = await session.execute(query)
        return result.scalars().all()

    async def set_admin(self, user: User, is_admin: bool):
        user.profile.is_admin = is_admin
