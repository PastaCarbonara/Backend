import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from app.swipe_session.schemas.swipe import CreateSwipeSchema
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from app.user.services.user import UserService
from core.db import Transactional, session

from app.swipe_session.schemas.swipe_session import CreateSwipeSessionSchema
from core.db.models import SwipeSession
from core.helpers.hashids import check_id, decode


class SwipeSessionConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()

        # Check if session_id exists in db

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        self.active_connections[session_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, session_id: str, message: str):

        # store message?

        for connection in self.active_connections[session_id]:
            await connection.send_text(message)


class SwipeSessionService:
    def __init__(self) -> None:
        ...

    async def handler(self, websocket: WebSocket, session_id: str, user_id: int):
        user_id = check_id(user_id, UserService().get_user_by_id)
        session_id = check_id(session_id, self.get_swipe_session_by_id)

        await manager.connect(websocket, session_id)

        if not user_id or not session_id:
            await manager.send_personal_message('{"message": "Invalid ID"}', websocket)
            manager.disconnect(session_id, websocket)
            return
        
        await manager.send_personal_message('{"message": "You have connected!!"}', websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast(session_id, data)

        except WebSocketDisconnect:
            manager.disconnect(session_id, websocket)
            await manager.broadcast(session_id, '{"message": f"Client '+str(user_id)+' left the chat"}')

    async def get_swipe_session_list(self) -> List[SwipeSession]:
        query = (
            select(SwipeSession)
            .options(
                joinedload(SwipeSession.swipes)
            )
        )

        result = await session.execute(query)
        return result.unique().scalars().all()

    async def get_swipe_session_by_id(self, session_id) -> SwipeSession:
        query = (
            select(SwipeSession)
            .where(SwipeSession.id == session_id)
            .options(
                joinedload(SwipeSession.swipes),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()

    @Transactional()
    async def create_swipe_session(self, request: CreateSwipeSessionSchema):
        db_swipe_session = SwipeSession(**request.dict())

        session.add(db_swipe_session)
        await session.flush()

        return db_swipe_session.id

    async def create_swipe(self, swipe: CreateSwipeSchema):
        ...


manager = SwipeSessionConnectionManager()
