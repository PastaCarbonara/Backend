from typing import List
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
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

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

    async def deny(self, websocket: WebSocket, msg: str = "Access denied"):
        """Denies access to the websocket"""
        await websocket.accept()
        await websocket.send_text('{"message": "' + f"{msg}" + '"}')
        await websocket.close(status.WS_1000_NORMAL_CLOSURE)

    def disconnect(self, session_id: str, websocket: WebSocket) -> bool:
        """Returns a bool wether or not there are still connections active"""
        
        self.active_connections[session_id].remove(websocket)

        if len(self.active_connections[session_id]) == 0:
            del self.active_connections[session_id]
            return False
        
        return True

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, session_id: str, message: str):
        for connection in self.active_connections[session_id]:
            await connection.send_text(message)


class SwipeSessionService:
    def __init__(self) -> None:
        ...

    async def handler(self, websocket: WebSocket, session_id: str, user_id: int):
        try:
            user = await check_id(user_id, UserService().get_user_by_id)
            session = await check_id(session_id, self.get_swipe_session_by_id)
        except:
            await manager.deny(websocket, "Invalid ID")
            return
        
        await manager.connect(websocket, session.id)

        if not user or not session:
            await manager.send_personal_message('{"message": "Invalid ID"}', websocket)
            manager.disconnect(session.id, websocket)
            return
        
        await manager.send_personal_message('{"message": "You have connected!!"}', websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast(session.id, data)

        except WebSocketDisconnect:
            if manager.disconnect(session.id, websocket):
                await manager.broadcast(session.id, '{"message": f"Client '+str(user_id)+' left the chat"}')

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
