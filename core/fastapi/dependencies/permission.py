from abc import ABC, abstractmethod
import json
from typing import List, Type

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase
from app.group.services.group import GroupService

from app.user.services import UserService
from core.exceptions import (
    CustomException,
    UnauthorizedException,
    MissingUserIDException,
    MissingGroupIDException,
)
from core.helpers.hashids import decode_single


async def provides_hashed_id(request, param_name):
    """Checks and converts ID from hash to int"""

    if param_name in request.path_params:
        param_id = decode_single(request.path_params[param_name])
        request.path_params[param_name] = str(param_id)

    else:
        try:
            data = await request.json()

        except json.JSONDecodeError:
            return False

        if not data.get(param_name):
            return False

        param_id = decode_single(data.get(param_name))
        data[param_name] = str(param_id)

        new_body = json.dumps(data, indent=2).encode("utf-8")
        request.body = new_body

    return True


class BasePermission(ABC):
    exception = CustomException

    @abstractmethod
    async def has_permission(self, request: Request) -> bool:
        pass


class IsAuthenticated(BasePermission):
    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        return request.user.id is not None


class IsAdmin(BasePermission):
    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        user_id = request.user.id
        if not user_id:
            return False

        return await UserService().is_admin(user_id=user_id)


class AllowAll(BasePermission):
    async def has_permission(self, request: Request) -> bool:
        return True


class ProvidesUserID(BasePermission):
    exception = MissingUserIDException

    async def has_permission(self, request: Request) -> bool:
        try:
            data = await request.json()

        except json.JSONDecodeError:
            return False

        # if user is logged in AND admin: can input user_id
        # if user is logged in NOT admin: just use their id
        # if user is NOT logged in: can input user_id

        if request.user.id is None:
            return data.get("user_id")

        elif await UserService().is_admin(user_id=request.user.id):
            if not data.get("user_id"):
                data["user_id"] = request.user.id
                new_body = json.dumps(data, indent=2).encode("utf-8")
                request.body = new_body

        return True


class ProvidesGroupID(BasePermission):
    exception = MissingGroupIDException

    async def has_permission(self, request: Request) -> bool:
        return await provides_hashed_id(request, "group_id")


class IsGroupMember(BasePermission):
    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        user_id = request.user.id

        if not user_id:
            return False

        if "group_id" not in request.path_params:
            return False

        try:
            group_id = int(request.path_params["group_id"])
        except ValueError:
            raise ValueError(
                "invalid literal for int() with base 10: '"
                + request.path_params["group_id"]
                + "'. Did you forget to put 'ProvidesGroupID' in the permission dependencies?"
            )
        print(group_id, user_id)

        return await GroupService().is_member(group_id=group_id, user_id=user_id)


class IsGroupAdmin(BasePermission):
    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        user_id = request.user.id
        if not user_id:
            return False

        return True


class PermissionDependency(SecurityBase):
    def __init__(self, permissions: List[Type[BasePermission]]):
        self.permissions = permissions
        self.model: APIKey = APIKey(**{"in": APIKeyIn.header}, name="Authorization")
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request):
        for permission in self.permissions:
            cls = permission()
            if not await cls.has_permission(request=request):
                raise cls.exception
