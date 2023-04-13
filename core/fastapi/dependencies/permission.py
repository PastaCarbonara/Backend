from abc import ABC, abstractmethod
import json
from typing import List, Type

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase
from app.group.services.group import GroupService
from app.swipe_session.services.swipe_session import SwipeSessionService

from app.user.services import UserService
from core.exceptions import (
    CustomException,
    UnauthorizedException,
    MissingUserIDException,
    MissingGroupIDException,
)
from core.helpers.hashid import decode_single


def get_hashed_id_from_path(request):
    hashed_id = request.path_params.get("hashed_id")
    if not hashed_id:
        return None
    
    return decode_single(hashed_id)


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


class IsGroupMember(BasePermission):
    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        user_id = request.user.id

        if not user_id:
            return False

        group_id = get_hashed_id_from_path(request)
        if not group_id:
            return False
        
        try:
            group_id = int(group_id)
        except ValueError as e:
            raise ValueError(str(e) + " did you forget to decode?")

        return await GroupService().is_member(group_id=group_id, user_id=user_id)


class IsGroupAdmin(BasePermission):
    exception = UnauthorizedException

    async def has_permission(self, request: Request) -> bool:
        user_id = request.user.id
        if not user_id:
            return False

        group_id = get_hashed_id_from_path(request)
        if not group_id:
            return False

        try:
            group_id = int(group_id)
        except ValueError as e:
            raise ValueError(str(e) + " did you forget to decode?")

        return await GroupService().is_admin(group_id=group_id, user_id=user_id)


class PermissionDependency(SecurityBase):
    def __init__(self, permissions: List[List[Type[BasePermission]]]):
        self.permissions = permissions
        self.model: APIKey = APIKey(**{"in": APIKeyIn.header}, name="Authorization")
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request):
        exceptions = {}
        for i, permission_combo in enumerate(self.permissions):
            exceptions[i] = []

            for permission in permission_combo:
                cls = permission()
                if not await cls.has_permission(request=request):
                    exceptions[i].append(cls.exception)

        if any(len(exceptions[i]) == 0 for i in exceptions):
            return

        for i in exceptions:
            if len(exceptions[i]) > 0:
                raise exceptions[i][0]
