from typing import List

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from core.fastapi_versioning.versioning import version
from core.helpers.socket import manager
from core.helpers.redis import redis as rds
import json
import asyncio


swipe_session_v1_router = APIRouter()


@swipe_session_v1_router.get("")
@version(1)
async def test():
    return ":D"


@swipe_session_v1_router.on_event("startup")
async def subscribe():
    print("started")
    asyncio.create_task(manager.consume())


@swipe_session_v1_router.websocket("/{application}/{client_id}/")
async def websocket_endpoint(websocket: WebSocket, application: str, client_id: str):
    print("attempt connection")
    await manager.connect(websocket, application, client_id)
    while True:
        try:
            data = await websocket.receive_json()
            print(f"received: {data}")
            rds.publish(
                'channel',
                json.dumps({
                   'application': application,
                   'client_id': client_id,
                   'message': data
                })
            )
        except WebSocketDisconnect:
            manager.disconnect(websocket, application, client_id)
        except RuntimeError:
            break
