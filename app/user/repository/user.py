from typing import List
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import joinedload
from core.db.models import User, UserProfile
from core.db import session
from app.user.exception.user import DuplicateUsernameException
from app.user.utils import get_password_hash


class UserRepository:
    async def create_user(self, username: str, hashed_pwd: str) -> None:
        user = User()
        session.add(user)
        await session.flush()

        user_profile = UserProfile(
            user_id=user.id, username=username, password=hashed_pwd
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

    async def get_user_by_username(self, username: str) -> User:
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
            .where(UserProfile.username == username)
            .options(joinedload(User.profile))
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_user_list(self) -> List[UserProfile]:
        """Get user list.

        Returns
        -------
        List[UserProfile]
            User list.
        """
        query = select(User).options(joinedload(User.profile))
        result = await session.execute(query)
        return result.scalars().all()

    async def set_admin(self, user: User, is_admin: bool):
        user.profile.is_admin = is_admin
