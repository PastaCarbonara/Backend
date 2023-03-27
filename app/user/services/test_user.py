from fastapi import Response
import pytest
from .user import UserService
from typing import List

import pytest

from app.user.services import UserService
from core.db import session
from core.db.models import User
from core.exceptions import (
    DuplicateUsernameException,
    UserNotFoundException,
    IncorrectPasswordException,
)


@pytest.fixture
def service() -> UserService:
    return UserService()


@pytest.fixture
@pytest.mark.asyncio
async def user(service) -> User:
    users = await service.get_user_list()
    if len(users) == 0:
        await service.create_user(username="testuser", password="testpassword")
    return await service.get_user_list()[0]


@pytest.mark.asyncio
async def test_get_user_list(service):
    result = await service.get_user_list()
    assert isinstance(result, List[User])


@pytest.mark.asyncio
async def test_get_user_by_id(service, user):
    user_id = await user.id
    result = await service.get_user_by_id(user_id)
    assert isinstance(result, User)
    assert user_id == result.id


# @pytest.mark.asyncio
# async def test_create_user(service):
#     await service.create_user(username="newuser", password="newpassword")
#     result = await service.get_user_list()
#     assert len(result) == 1
#     assert result[0].username == "newuser"
#     assert result[1].password == "newpassword"


# @pytest.mark.asyncio
# async def test_create_user_duplicate(service):
#     await service.create_user(username="testuser", password="testpassword")
#     with pytest.raises(DuplicateUsernameException):
#         await service.create_user(username="testuser", password="testpassword")


# @pytest.mark.asyncio
# async def test_is_admin(service, user):
#     assert await service.is_admin(user.user_id) == False


# @pytest.mark.asyncio
# async def test_login(service, user):
#     response = await service.login(username="testuser", password="testpassword")
#     assert response.access_token is not None
#     assert response.refresh_token is not None


# @pytest.mark.asyncio
# async def test_login_incorrect_password(service, user):
#     with pytest.raises(IncorrectPasswordException):
#         await service.login(username="testuser", password="wrongpassword")


# @pytest.mark.asyncio
# async def test_login_user_not_found(service):
#     with pytest.raises(UserNotFoundException):
#         await service.login(username="nonexistentuser", password="password")


# @pytest.mark.asyncio
# async def test_verify_password(service):
#     password = "testpassword"
#     hashed_password = service.get_password_hash(password)
#     assert service.verify_password(password, hashed_password) == True
#     assert service.verify_password("wrongpassword", hashed_password) == False