from typing import List

from fastapi import APIRouter, Depends, Query
from core.fastapi_versioning.versioning import version

from api.user.v1.request.user import LoginRequest
from api.user.v1.response.user import LoginResponse
from app.user.schemas import (
    ExceptionResponseSchema,
    GetUserListResponseSchema,
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
    response_model=List[GetUserListResponseSchema],
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAdmin]))],
)
@version(1)
async def get_user_list(
    limit: int = Query(10, description="Limit"),
    prev: int = Query(None, description="Previous ID"),
):
    return await UserService().get_user_list(limit=limit, prev=prev)


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
