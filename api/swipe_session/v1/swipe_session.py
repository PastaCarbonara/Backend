from typing import List

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from core.fastapi_versioning.versioning import version
from core.helpers.socket import manager


swipe_session_v1_router = APIRouter()


@swipe_session_v1_router.get("")
@version(1)
async def test():
    return ":D"

    
@swipe_session_v1_router.websocket("/{swipe_session_id}/{client_id}")
@version(1)
async def websocket_endpoint(websocket: WebSocket, swipe_session_id: int, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast({"message": f"{data}", "client_id": client_id})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({"message": f"Client left the chat", "client_id": client_id})
