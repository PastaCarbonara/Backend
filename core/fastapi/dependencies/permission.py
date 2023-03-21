from abc import ABC, abstractmethod
import json
from typing import List, Type

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase

from app.user.services import UserService
from core.exceptions import CustomException, UnauthorizedException, MissingUserIDException


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
                new_body = json.dumps(data, indent=2).encode('utf-8')
                request.body = new_body

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
