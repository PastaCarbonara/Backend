from typing import List

from fastapi import APIRouter, Depends, Query
from app.group.schemas.group import GroupSchema
from app.group.services.group import GroupService
from core.exceptions import ExceptionResponseSchema
from core.fastapi.dependencies.hashid import decode_path_id
from core.fastapi.dependencies.permission import IsAuthenticated, IsUserOwner
from core.fastapi.dependencies.user import get_current_user
from core.fastapi_versioning.versioning import version

from api.user.v1.request.user import LoginRequest
from api.user.v1.response.user import LoginResponse
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


@user_v1_router.post(
    "/login",
    response_model=LoginResponse,
    responses={"404": {"model": ExceptionResponseSchema}},
)
@version(1)
async def login(request: LoginRequest):
    token = await UserService().login(username=request.username, password=request.password)
    return {"access_token": token.access_token, "refresh_token": token.refresh_token}


@user_v1_router.get(
    "/{hashed_id}/groups",
    response_model=list[GroupSchema],
    dependencies=[Depends(PermissionDependency([[IsAdmin], [IsAuthenticated, IsUserOwner]]))]
)
@version(1)
async def get_user_groups(user_id: int = Depends(decode_path_id)):
    return await GroupService().get_groups_by_user(user_id)
