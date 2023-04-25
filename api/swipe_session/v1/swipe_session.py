from typing import List

from fastapi import APIRouter, Depends, Query, Request, WebSocket
from app.swipe_session.repository.swipe_session import SwipeSessionRepository
from app.swipe_session.schemas.swipe_session import (
    ActionDocsSchema,
    CreateSwipeSessionSchema,
    SwipeSessionSchema,
    UpdateSwipeSessionSchema,
)
from app.swipe_session.services.swipe_session import SwipeSessionService
from app.swipe_session.services.swipe_session_websocket import (
    SwipeSessionWebsocketService,
)

from core.exceptions import ExceptionResponseSchema
from core.fastapi.dependencies import (
    AllowAll,
    IsAdmin,
    PermissionDependency,
    IsGroupAdmin,
    IsAuthenticated,
)
from core.fastapi.dependencies.permission import IsAuthenticated, IsSessionOwner
from core.fastapi.dependencies.user import get_current_user
from core.fastapi_versioning.versioning import version


swipe_session_v1_router = APIRouter()


@swipe_session_v1_router.websocket("/{session_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str):
    await SwipeSessionWebsocketService().handler(websocket, session_id, user_id)


@swipe_session_v1_router.get(
    "/actions_docs",
    response_model=ActionDocsSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
@version(1)
async def get_swipe_session_actions():
    return ActionDocsSchema(
        actions=await SwipeSessionService().get_swipe_session_actions()
    )


@swipe_session_v1_router.get(
    "",
    response_model=List[SwipeSessionSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin]]))],
)
@version(1)
async def get_swipe_sessions():
    return await SwipeSessionService().get_swipe_session_list()


@swipe_session_v1_router.post(
    "",
    response_model=SwipeSessionSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAuthenticated]]))],
)
@version(1)
async def create_swipe_session(
    request: CreateSwipeSessionSchema, user=Depends(get_current_user)
):
    """Create a personal swipe session, no group"""
    session_id = await SwipeSessionService().create_swipe_session(request, user)
    return await SwipeSessionService().get_swipe_session_by_id(session_id)


@swipe_session_v1_router.patch(
    "",
    response_model=SwipeSessionSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([[IsAdmin], [IsSessionOwner]]))],
)
@version(1)
async def update_swipe_session(
    request: UpdateSwipeSessionSchema, user=Depends(get_current_user)
):
    session_id = await SwipeSessionService().update_swipe_session(request, user)
    return await SwipeSessionService().get_swipe_session_by_id(session_id)
