from typing import List

from fastapi import APIRouter, Depends, Query
from app.group.schemas.group import GroupSchema
from app.group.services.group import GroupService
from core.exceptions import ExceptionResponseSchema
from core.fastapi.dependencies.hashid import get_path_user_id
from core.fastapi.dependencies.permission import IsAuthenticated, IsUserOwner
from core.fastapi.dependencies.user import get_current_user
from core.fastapi_versioning.versioning import version

from app.user.schemas import (
    UserSchema,
    CreateUserRequestSchema,
    CreateUserResponseSchema,
)
from app.user.services import UserService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAdmin,
)

user_v1_router = APIRouter()


@user_v1_router.get(
    "",
    response_model=List[UserSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def get_user_list():
    return await UserService().get_user_list()


@user_v1_router.post(
    "",
    response_model=CreateUserResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
@version(1)
async def create_user(request: CreateUserRequestSchema):
    await UserService().create_user(**request.dict())
    return {"username": request.username}


@user_v1_router.get(
    "/{user_id}/groups",
    response_model=list[GroupSchema],
    dependencies=[Depends(PermissionDependency([[IsAdmin], [IsAuthenticated, IsUserOwner]]))]
)
@version(1)
async def get_user_groups(user_id: int = Depends(get_path_user_id)):
    return await GroupService().get_groups_by_user(user_id)
