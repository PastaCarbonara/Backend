from datetime import date, datetime
import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
from pydantic import ValidationError
from sqlalchemy import or_, select, and_, update
from sqlalchemy.orm import joinedload
from app.group.services.group import GroupService
from app.recipe.schemas.recipe import GetFullRecipeResponseSchema
from app.recipe.services.recipe import RecipeService
from app.swipe.services.swipe import SwipeService
from app.user.services.user import UserService
from core.db import Transactional, session

from app.swipe.schemas.swipe import CreateSwipeSchema
from app.swipe_session.schemas.swipe_session import (
    CreateSwipeSessionSchema,
    PacketSchema,
    UpdateSwipeSessionSchema,
)
from core.db.enums import SwipeSessionActionEnum as ACTIONS, SwipeSessionEnum
from core.db.models import SwipeSession
from core.exceptions.base import UnauthorizedException
from core.exceptions.recipe import RecipeNotFoundException
from core.exceptions.swipe_session import SwipeSessionNotFoundException
from core.helpers.hashids import check_id, decode, decode_single


class SwipeSessionConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

    async def deny(self, websocket: WebSocket, msg: str = "Access denied") -> None:
        """Denies access to the websocket"""
        await websocket.accept()
        await SwipeSessionService().handle_connection_code(websocket, 400, msg)
        await websocket.close(status.WS_1000_NORMAL_CLOSURE)

    def disconnect(self, session_id: str, websocket: WebSocket) -> bool:
        """Returns a bool wether or not there are still connections active"""

        self.active_connections[session_id].remove(websocket)

        if self.get_connection_count(session_id) == 0:
            del self.active_connections[session_id]
            return False

        return True

    async def personal_packet(self, websocket: WebSocket, packet: PacketSchema) -> None:
        await websocket.send_json(packet.dict())

    async def global_broadcast(self, packet: PacketSchema) -> None:
        for session_id in self.active_connections.keys():
            for connection in self.active_connections[session_id]:
                await connection.send_json(packet.dict())

    async def session_broadcast(self, session_id: str, packet: PacketSchema) -> None:
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

    async def handler(
        self, websocket: WebSocket, session_id: str, user_id: int
    ) -> None:
        message = "Invalid ID"
        try:
            user = await check_id(user_id, UserService().get_user_by_id)
            session = await check_id(session_id, self.get_swipe_session_by_id)
        except:
            await manager.deny(websocket, message)
            return

        if session.group_id:
            if not await GroupService().is_member(session.group_id, user.id):
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
                # NOTE NOTE NOTE NOTE!!!! DO NOTTTTT 'RETURN' IF YOU WISH TO 'CONTINUE'
                # Learned it the hard way, took me a day.

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
                if packet.action == ACTIONS.GLOBAL_MESSAGE:
                    if not await UserService().is_admin(user.id):
                        message = "Unauthorized"
                        await self.handle_connection_code(websocket, 401, message)
                        continue
                    await self.handle_global_message(
                        websocket, packet.payload.get("message")
                    )

                elif packet.action == ACTIONS.RECIPE_SWIPE:
                    await self.handle_recipe_swipe(websocket, session, user.id, packet)

                elif packet.action == ACTIONS.SESSION_MESSAGE:
                    await self.handle_session_message(
                        websocket, session.id, packet.payload.get("message")
                    )

                elif packet.action == ACTIONS.SESSION_STATUS_UPDATE:
                    if not await GroupService().is_admin(session.group_id, user.id):
                        message = "Unauthorized"
                        await self.handle_connection_code(websocket, 401, message)
                        continue
                    await self.handle_session_status_update(
                        websocket, session.id, user.id, packet.payload.get("status")
                    )

                else:
                    message = "Action is not implemented or not available"
                    await self.handle_connection_code(websocket, 501, message)

        except WebSocketDisconnect:
            if manager.disconnect(session.id, websocket):
                await self.handle_session_message(
                    websocket, session.id, f"Client {user_id} left the session"
                )

    async def handle_session_status_update(
        self, websocket: WebSocket, session_id: int, user_id: int, status: str
    ):
        if not status in [e.value for e in SwipeSessionEnum]:
            await self.handle_connection_code(websocket, 400, "Incorrect status")
            return

        await self.update_swipe_session(
            UpdateSwipeSessionSchema(
                id=session_id, status=SwipeSessionEnum.COMPLETED, user_id=user_id
            )
        )

        payload = {"status": status}
        packet = PacketSchema(action=ACTIONS.SESSION_STATUS_UPDATE, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def handle_global_message(self, websocket: WebSocket, message: str) -> None:
        if not message:
            await self.handle_connection_code(websocket, 400, "No message provided")
            return

        payload = {"message": message}
        packet = PacketSchema(action=ACTIONS.GLOBAL_MESSAGE, payload=payload)

        await self.handle_global_packet(packet)

    async def handle_global_packet(self, packet: PacketSchema) -> None:
        await manager.global_broadcast(packet)

    async def handle_session_message(
        self, websocket: WebSocket, session_id: int, message: str
    ) -> None:
        if not message:
            await self.handle_connection_code(websocket, 400, "No message provided")
            return

        payload = {"message": message}
        packet = PacketSchema(action=ACTIONS.SESSION_MESSAGE, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def handle_session_packet(
        self, session_id: int, packet: PacketSchema
    ) -> None:
        await manager.session_broadcast(session_id, packet)

    async def handle_connection_code(self, websocket, code: int, message: str) -> None:
        payload = {"status_code": code, "message": message}
        packet = PacketSchema(action=ACTIONS.CONNECTION_CODE, payload=payload)

        await manager.personal_packet(websocket, packet)

    async def handle_recipe_swipe(
        self,
        websocket: WebSocket,
        session: SwipeSession,
        user_id: int,
        packet: PacketSchema,
    ) -> None:
        try:
            swipe_schema = CreateSwipeSchema(
                swipe_session_id=session.id, user_id=user_id, **packet.payload
            )

        except ValidationError as e:
            await self.handle_connection_code(websocket, 400, e.json())
            return

        recipe = await RecipeService().get_recipe_by_id(packet.payload["recipe_id"])
        if not recipe:
            await self.handle_connection_code(
                websocket, 404, RecipeNotFoundException.message
            )
            return

        existing_swipe = await SwipeService().get_swipe_by_creds(
            swipe_session_id=session.id,
            user_id=user_id,
            recipe_id=packet.payload["recipe_id"],
        )

        if existing_swipe:
            message = "This user has already swiped this recipe in this session"
            await self.handle_connection_code(websocket, 409, message)
            return

        new_swipe_id = await SwipeService().create_swipe(swipe_schema)

        matching_swipes = (
            await SwipeService().get_swipes_by_session_id_and_recipe_id_and_like(
                swipe_session_id=session.id,
                recipe_id=packet.payload["recipe_id"],
                like=True,
            )
        )

        group = await GroupService().get_group_by_id(session.group_id)

        if len(matching_swipes) >= len(group.users):
            await self.handle_session_match(
                websocket, session.id, packet.payload["recipe_id"]
            )
            await self.handle_session_status_update(
                websocket, session.id, user_id, SwipeSessionEnum.COMPLETED
            )

    async def handle_session_match(
        self, websocket: WebSocket, session_id: int, recipe_id: int
    ) -> None:
        recipe = await RecipeService().get_recipe_by_id(recipe_id)
        if not recipe:
            await self.handle_connection_code(
                websocket, 404, RecipeNotFoundException.message
            )
            return

        full_recipe = GetFullRecipeResponseSchema(**recipe.__dict__)

        payload = {"message": "A match has been found", "recipe": full_recipe}
        packet = PacketSchema(action=ACTIONS.RECIPE_MATCH, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def get_swipe_session_list(self) -> List[SwipeSession]:
        query = select(SwipeSession).options(joinedload(SwipeSession.swipes))

        result = await session.execute(query)
        return result.unique().scalars().all()

    async def get_swipe_session_by_id(self, session_id: int) -> SwipeSession:
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
    async def update_swipe_session(self, request: UpdateSwipeSessionSchema) -> int:
        try:
            request.id = int(request.id)
        except:
            request.id = decode_single(request.id)

        if type(request.session_date) == date:
            request.session_date = datetime.combine(request.session_date, datetime.min.time())
        else:
            if not request.session_date:
                request.session_date = datetime.now()

            request.session_date = request.session_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        swipe_session = await SwipeSessionService().get_swipe_session_by_id(request.id)

        if not request.status:
            request.status = swipe_session.status

        if not swipe_session:
            raise SwipeSessionNotFoundException

        if not await GroupService().is_admin(swipe_session.group_id, request.user_id):
            raise UnauthorizedException

        del request.user_id

        query = (
            update(SwipeSession)
            .where(SwipeSession.id == request.id)
            .values(**request.dict())
        )
        await session.execute(query)

        return swipe_session.id

    @Transactional()
    async def create_swipe_session(self, request: CreateSwipeSessionSchema) -> int:
        request.group_id = int(request.group_id)
        db_swipe_session = SwipeSession(**request.dict())

        if not request.session_date:
            request.session_date = datetime.now()

        request.session_date = request.session_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        session.add(db_swipe_session)
        await session.flush()

        return db_swipe_session.id

    async def get_swipe_session_actions(self) -> dict:
        from .action_docs import actions

        return actions


manager = SwipeSessionConnectionManager()
