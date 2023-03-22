import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
from pydantic import ValidationError
from sqlalchemy import or_, select, and_
from sqlalchemy.orm import joinedload
from app.recipe.schemas.recipe import GetFullRecipeResponseSchema
from app.recipe.services.recipe import RecipeService
from app.swipe.services.swipe import SwipeService
from app.user.services.user import UserService
from core.db import Transactional, session

from app.swipe.schemas.swipe import CreateSwipeSchema
from app.swipe_session.schemas.swipe_session import (
    CreateSwipeSessionSchema,
    PacketSchema,
)
from core.db.enums import SwipeSessionActionEnum as ACTIONS
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
        await SwipeSessionService.handle_connection_code(websocket, 400, msg)
        await websocket.close(status.WS_1000_NORMAL_CLOSURE)

    def disconnect(self, session_id: str, websocket: WebSocket) -> bool:
        """Returns a bool wether or not there are still connections active"""

        self.active_connections[session_id].remove(websocket)

        if len(self.active_connections[session_id]) == 0:
            del self.active_connections[session_id]
            return False

        return True

    async def send_personal_message(self, websocket: WebSocket, packet: PacketSchema):
        await websocket.send_json(packet.dict())

    async def global_broadcast(self, packet: PacketSchema):
        for session_id in self.active_connections.keys():
            for connection in self.active_connections[session_id]:
                await connection.send_json(packet.dict())

    async def session_broadcast(self, session_id: str, packet: PacketSchema):
        for connection in self.active_connections[session_id]:
            await connection.send_json(packet.dict())

    def get_connection_count(self, session_id: str | None = None) -> int:
        """Get total amount of WebSocket active connections

        Provide a session_id to get the amount for one session
        """
        if session_id:
            try:
                connections = self.active_connections[session_id]
            except KeyError:
                # Perhaps a better way to resolve this exists, as this might be unclear
                return 0

            return len(connections)

        total = 0
        for session in self.active_connections:
            total += len(self.active_connections[session])

        return total


class SwipeSessionService:
    def __init__(self) -> None:
        ...

    async def handler(self, websocket: WebSocket, session_id: str, user_id: int):
        message = "Invalid ID"
        try:
            user = await check_id(user_id, UserService().get_user_by_id)
            session = await check_id(session_id, self.get_swipe_session_by_id)
        except:
            await manager.deny(websocket, message)
            return

        await manager.connect(websocket, session.id)

        if not user or not session:
            await self.handle_connection_code(websocket, 400, message)
            manager.disconnect(session.id, websocket)
            return

        message = "You have connected"
        await self.handle_connection_code(websocket, 200, message)

        try:
            while True:
                data = await websocket.receive_text()

                # Gate keepers/Guard clauses
                try:
                    data_json = json.loads(data)
                except:
                    message = "Data is not JSON serializable"
                    await self.handle_connection_code(websocket, 400, message)
                    continue

                try:
                    packet = PacketSchema(**data_json)
                except ValidationError:
                    message = "Action does not exist"
                    await self.handle_connection_code(websocket, 400, message)
                    continue

                # Handlers
                if packet.action == ACTIONS.REQUEST_GLOBAL_MESSAGE:
                    # Add authorization check
                    await self.handle_global_packet(packet)

                elif packet.action == ACTIONS.REQUEST_RECIPE_LIKE:
                    await self.handle_recipe_like(
                        websocket, session.id, user.id, packet
                    )

                elif packet.action == ACTIONS.REQUEST_SESSION_MESSAGE:
                    await self.handle_session_packet(session.id, packet)

                else:
                    message = "Action is not implemented or not available"
                    await self.handle_connection_code(websocket, 501, message)

        except WebSocketDisconnect:
            if manager.disconnect(session.id, websocket):
                await self.handle_session_message(
                    session.id, f"Client {user_id} left the chat"
                )

    async def handle_global_message(self, message: str):
        payload = {"message": message}
        packet = PacketSchema(action=ACTIONS.RESPONSE_SESSION_MESSAGE, payload=payload)

        await self.handle_global_packet(packet)

    async def handle_global_packet(self, packet: PacketSchema):
        await manager.global_broadcast(packet)

    async def handle_session_message(self, session_id: int, message: str):
        payload = {"message": message}
        packet = PacketSchema(action=ACTIONS.RESPONSE_SESSION_MESSAGE, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def handle_session_packet(self, session_id: int, packet: PacketSchema):
        await manager.session_broadcast(session_id, packet)

    async def handle_connection_code(self, websocket, code: int, message: str):
        payload = {"code": code, "message": message}
        packet = PacketSchema(action=ACTIONS.RESPONSE_CONNECTION_CODE, payload=payload)

        await manager.send_personal_message(websocket, packet)

    async def handle_recipe_like(
        self, websocket: WebSocket, session_id: int, user_id: int, packet: PacketSchema
    ):
        try:
            swipe_schema = CreateSwipeSchema(
                swipe_session_id=session_id, user_id=user_id, **packet.payload
            )

        except ValidationError as e:
            await self.handle_connection_code(websocket, 400, e.json())
            return

        # Commented out for frontend testing

        # existing_swipe = await SwipeService().get_swipe_by_creds(
        #     swipe_session_id=session_id,
        #     user_id=user_id,
        #     recipe_id=packet.payload["recipe_id"]
        # )

        # if existing_swipe:
        #     message = "This user has already swiped this recipe in this session"
        #     await self.handle_connection_code(websocket, 409, message)
        #     return

        new_swipe_id = await SwipeService().create_swipe(swipe_schema)

        swipe_matches = await SwipeService().get_swipe_matches(
            swipe_session_id=session_id, recipe_id=packet.payload["recipe_id"]
        )

        # NOTE: Should check for amount of group members instead
        member_count = manager.get_connection_count(session_id)

        if len(swipe_matches) + 1 >= member_count:
            await self.handle_session_match(session_id, packet.payload["recipe_id"])

    async def handle_session_match(self, session_id, recipe_id):
        recipe = await RecipeService().get_recipe_by_id(recipe_id)
        full_recipe = GetFullRecipeResponseSchema(**recipe.__dict__)

        payload = {"message": "A match has been found", "recipe": full_recipe}
        packet = PacketSchema(action=ACTIONS.RESPONSE_RECIPE_MATCH, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def get_swipe_session_list(self) -> List[SwipeSession]:
        query = select(SwipeSession).options(joinedload(SwipeSession.swipes))

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


manager = SwipeSessionConnectionManager()
