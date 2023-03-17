from typing import List

from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketDisconnect
from app.swipe_session.services.swipe_session import SwipeSessionService
from core.fastapi.dependencies.permission import AllowAll, PermissionDependency, ProvidesUserID
from core.fastapi_versioning.versioning import version


swipe_session_v1_router = APIRouter()


@swipe_session_v1_router.get("")
@version(1)
async def test():
    return ":D"


@swipe_session_v1_router.websocket("/{session_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str):
    print(websocket.cookies)
    await SwipeSessionService().handler(websocket, session_id, user_id)
