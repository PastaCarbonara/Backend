from typing import Optional, List

from sqlalchemy import or_, select, and_

from core.db.models import User, UserProfile
from app.user.schemas.user import LoginResponseSchema
from core.db import Transactional, session
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateUsernameException,
    UserNotFoundException,
)
from core.utils.token_helper import TokenHelper


class UserService:
    def __init__(self):
        ...

    async def get_user_list(
        self,
        limit: int = 12,
        prev: Optional[int] = None,
    ) -> List[UserProfile]:
        query = select(UserProfile)

        if prev:
            query = query.where(UserProfile.user_id < prev)

        if limit > 12:
            limit = 12

        query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @Transactional()
    async def create_user(
        self, username: str, password: str
    ) -> None:

        query = select(User).where(or_(UserProfile.username == username))
        result = await session.execute(query)
        is_exist = result.scalars().first()
        if is_exist:
            raise DuplicateUsernameException

        user = User()
        session.add(user)
        await session.flush()
        await session.refresh(user)

        user_profile = UserProfile(user_id=user.id, username=username, password=password)
        session.add(user_profile)

    async def is_admin(self, user_id: int) -> bool:
        result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        user = result.scalars().first()
        if not user:
            return False

        if user.is_admin is False:
            return False

        return True

    async def login(self, username: str, password: str) -> LoginResponseSchema:
        result = await session.execute(
            select(UserProfile).where(and_(UserProfile.username == username, password == password))
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        response = LoginResponseSchema(
            token=TokenHelper.encode(payload={"user_id": user.user_id}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
        return response
