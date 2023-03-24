from typing import Optional, List

from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload

from core.db.models import User, UserProfile
from app.user.schemas.user import LoginResponseSchema
from core.db import Transactional, session
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateUsernameException,
    UserNotFoundException,
    IncorrectPasswordException,
)
from core.utils.token_helper import TokenHelper
from passlib.context import CryptContext


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

    async def get_user_by_id(self, user_id: int) -> User:
        query = select(User).where(User.id == user_id).options(joinedload(User.profile))
        result = await session.execute(query)
        return result.scalars().first()

    @Transactional()
    async def create_user(self, username: str, password: str) -> None:

        query = select(User).where(or_(UserProfile.username == username))
        result = await session.execute(query)
        is_exist = result.scalars().first()
        if is_exist:
            raise DuplicateUsernameException
        hashed_pwd = self.get_password_hash(password)

        user = User()
        session.add(user)
        await session.flush()

        user_profile = UserProfile(
            user_id=user.id, username=username, password=hashed_pwd
        )
        session.add(user_profile)

    @Transactional()
    async def set_admin(user_id: int, is_admin: bool):
        user_query = select(User).where(User.id == user_id)
        result = await session.execute(user_query)
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException
        user.is_admin = is_admin

    async def is_admin(self, user_id: int) -> bool:
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        user = result.scalars().first()
        if not user:
            return False

        return user.is_admin

    async def login(self, username: str, password: str) -> LoginResponseSchema:
        result = await session.execute(
            select(UserProfile).where(and_(UserProfile.username == username))
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException

        if not self.verify_password(password, user.password):
            raise IncorrectPasswordException

        response = LoginResponseSchema(
            access_token=TokenHelper.encode(payload={"user_id": user.user_id}),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
        )
        return response

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
