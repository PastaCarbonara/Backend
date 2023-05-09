import json
from typing import List

from pydantic import ValidationError
from app.group.schemas.group import GroupSchema, CreateGroupSchema
from app.group.services.group import GroupService

from fastapi import APIRouter, Depends, Query, Request
from app.recipe.schemas.recipe import GetFullRecipeResponseSchema
from app.swipe_session.schemas.swipe_session import (
    CreateSwipeSessionSchema,
    SwipeSessionSchema,
    UpdateSwipeSessionSchema,
)
from app.swipe_session.services.swipe_session import SwipeSessionService
from core.exceptions import ExceptionResponseSchema, GroupNotFoundException
from core.exceptions.group import GroupJoinConflictException
from core.fastapi.dependencies.hashid import get_path_group_id, get_path_session_id
from core.fastapi.dependencies.object_storage import get_object_storage
from core.fastapi.dependencies.user import get_current_user
from core.fastapi_versioning import version


from core.fastapi.dependencies.permission import (
    AllowAll,
    IsGroupAdmin,
    PermissionDependency,
    IsAdmin,
    IsAuthenticated,
    IsGroupMember,
)


group_v1_router = APIRouter()


@group_v1_router.get(
    "",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=list[GroupSchema],
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
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
async def create_group(
    request: CreateGroupSchema,
    user=Depends(get_current_user),
    object_storage=Depends(get_object_storage),
):
    group_id = await GroupService().create_group(request, user.id, object_storage)
    return await GroupService().get_group_by_id(group_id)


@group_v1_router.get(
    "/{group_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
    response_model=GroupSchema,
    dependencies=[
        Depends(
            PermissionDependency([[IsAdmin], [IsAuthenticated, IsGroupMember]])
        )
    ],
)
@version(1)
async def get_group(group_id: int = Depends(get_path_group_id)):
    group = await GroupService().get_group_by_id(group_id)
    if not group:
        raise GroupNotFoundException

    return group


@group_v1_router.get(
    "/{group_id}/join",
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def join_group(request: Request, group_id: int = Depends(get_path_group_id)):
    if not await GroupService().is_member(group_id, request.user.id):
        return await GroupService().join_group(group_id, request.user.id)


@group_v1_router.get(
    "/{group_id}/swipe_sessions",
    response_model=list[SwipeSessionSchema],
    dependencies=[Depends(PermissionDependency([[IsAdmin], [IsAuthenticated, IsGroupMember]]))],
)
@version(1)
async def get_swipe_sessions_by_group(group_id: int = Depends(get_path_group_id)):
    return await SwipeSessionService().get_swipe_sessions_by_group(group_id)


@group_v1_router.post(
    "/{group_id}/swipe_sessions",
    response_model=SwipeSessionSchema,
    dependencies=[Depends(PermissionDependency([[IsAdmin], [IsAuthenticated, IsGroupAdmin]]))],
)
@version(1)
async def create_swipe_session(
    request: CreateSwipeSessionSchema,
    group_id: int = Depends(get_path_group_id),
    user=Depends(get_current_user),
):
    session_id = await SwipeSessionService().create_swipe_session(
        request, user, group_id
    )
    return await SwipeSessionService().get_swipe_session_by_id(session_id)


@group_v1_router.patch(
    "/{group_id}/swipe_sessions",
    response_model=SwipeSessionSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def update_swipe_session(
    request: UpdateSwipeSessionSchema,
    group_id: int = Depends(get_path_group_id),
    user=Depends(get_current_user),
):
    session_id = await SwipeSessionService().update_swipe_session(
        request, user, group_id
    )
    return await SwipeSessionService().get_swipe_session_by_id(session_id)


@group_v1_router.get(
    "/{group_id}/swipe_sessions/{session_id}/matches",
    response_model=GetFullRecipeResponseSchema,
    dependencies=[Depends(PermissionDependency([[IsAdmin], [IsAuthenticated, IsGroupMember]]))]
)
@version(1)
async def get_swipe_session_match(
    group_id: int = Depends(get_path_group_id),
    session_id: int = Depends(get_path_session_id),
):
    return await SwipeSessionService().get_matches(session_id)
