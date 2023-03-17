from typing import List

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from core.fastapi_versioning.versioning import version
from core.helpers.socket import manager
from core.helpers.redis import redis as rds
import json


swipe_session_v1_router = APIRouter()


@swipe_session_v1_router.get("")
@version(1)
async def test():
    return ":D"


@swipe_session_v1_router.websocket("/{application}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, application: str, client_id: int):
    await manager.connect(websocket, application)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", application)
    except WebSocketDisconnect:
        manager.disconnect(websocket, application)
        await manager.broadcast(f"Client #{client_id} left the chat", application)
