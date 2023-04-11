import json
from typing import List

from pydantic import ValidationError
from app.group.schemas.group import GroupSchema, CreateGroupSchema
from app.group.services.group import GroupService

from fastapi import APIRouter, Depends, Query, Request
from core.exceptions import ExceptionResponseSchema, GroupNotFoundException
from core.exceptions.group import GroupJoinConflictException
from core.fastapi.dependencies.hashid import decode_path_id
from core.fastapi_versioning import version


from core.fastapi.dependencies.permission import (
    AllowAll,
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
    IsGroupMember,
)


group_v1_router = APIRouter()


@group_v1_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=List[GroupSchema],
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def get_group_list():
    return await GroupService().get_group_list()


@group_v1_router.post(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GroupSchema,
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def create_group(request: CreateGroupSchema, http_request: Request):
    group_id = await GroupService().create_group(request, http_request.user.id)
    return await GroupService().get_group_by_id(group_id)


@group_v1_router.get(
    "/{group_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GroupSchema,
    dependencies=[
        Depends(PermissionDependency([[IsAdmin], [IsAuthenticated, IsGroupMember]]))
    ],
)
@version(1)
async def get_group(group_id: int = Depends(decode_path_id)):
    group = await GroupService().get_group_by_id(group_id)
    if not group:
        raise GroupNotFoundException

    return group


@group_v1_router.get(
    "/join/{group_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def join_group(request: Request, group_id: int = Depends(decode_path_id)):
    if not await GroupService().is_member(group_id, request.user.id):
        return await GroupService().join_group(group_id, request.user.id)
