import json
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
from pydantic import ValidationError
from app.group.services.group import GroupService
from app.recipe.schemas.recipe import GetFullRecipeResponseSchema
from app.recipe.services.recipe import RecipeService
from app.swipe.schemas.swipe import CreateSwipeSchema
from app.swipe.services.swipe import SwipeService
from app.swipe_session.exception.swipe_session import (
    AccessDeniedException,
    ActionNotFoundException,
    ActionNotImplementedException,
    AlreadySwipedException,
    ConnectionCode,
    InactiveException,
    InvalidIdException,
    JSONSerializableException,
    NoMessageException,
    StatusNotFoundException,
    SuccessfullConnection,
    ValidationException,
)
from app.user.services.user import UserService
from core.db.enums import SwipeSessionActionEnum as ACTIONS, SwipeSessionEnum
from app.swipe_session.schemas.swipe_session import (
    PacketSchema,
    UpdateSwipeSessionSchema,
)
from app.swipe_session.services.swipe_session import SwipeSessionService
from core.db.models import SwipeSession, User
from core.exceptions.base import CustomException, UnauthorizedException
from core.exceptions.recipe import RecipeNotFoundException
from core.helpers.hashid import check_id


class SwipeSessionConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

    async def deny(
        self, websocket: WebSocket, exception: CustomException = AccessDeniedException
    ) -> None:
        """Denies access to the websocket"""
        await websocket.accept()
        await SwipeSessionWebsocketService().handle_connection_code(
            websocket, exception
        )
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


class SwipeSessionWebsocketService:
    async def handler(
        self, websocket: WebSocket, session_id: str, user_id: int
    ) -> None:
        try:
            user = await check_id(user_id, UserService().get_user_by_id)
            session = await check_id(
                session_id, SwipeSessionService().get_swipe_session_by_id
            )
        except:
            await manager.deny(websocket, InvalidIdException)
            return
        
        if session.status != SwipeSessionEnum.IN_PROGRESS:
            await manager.deny(websocket, InactiveException)
            return

        if session.group_id:
            if not await GroupService().is_member(session.group_id, user.id):
                await manager.deny(websocket, InvalidIdException)
                return

        await manager.connect(websocket, session.id)

        if not user or not session:
            await self.handle_connection_code(websocket, InvalidIdException)
            manager.disconnect(session.id, websocket)
            return

        await self.handle_connection_code(websocket, SuccessfullConnection)

        try:
            while True:
                # NOTE NOTE NOTE NOTE!!!! DO NOTTTTT 'RETURN' IF YOU WISH TO 'CONTINUE'
                # Learned it the hard way, and took me a day.

                data = await websocket.receive_text()

                # Gate keepers/Guard clauses
                try:
                    data_json = json.loads(data)
                except:
                    await self.handle_connection_code(
                        websocket, JSONSerializableException
                    )
                    continue

                try:
                    packet = PacketSchema(**data_json)
                except ValidationError:
                    await self.handle_connection_code(
                        websocket, ActionNotFoundException
                    )
                    continue

                # Handlers
                if packet.action == ACTIONS.GLOBAL_MESSAGE:
                    if not await UserService().is_admin(user.id):
                        await self.handle_connection_code(
                            websocket, UnauthorizedException
                        )
                        continue
                    await self.handle_global_message(
                        websocket, packet.payload.get("message")
                    )

                elif packet.action == ACTIONS.RECIPE_SWIPE:
                    await self.handle_recipe_swipe(websocket, session, user, packet)

                elif packet.action == ACTIONS.SESSION_MESSAGE:
                    await self.handle_session_message(
                        websocket, session.id, packet.payload.get("message")
                    )

                elif packet.action == ACTIONS.SESSION_STATUS_UPDATE:
                    if not await GroupService().is_admin(session.group_id, user.id):
                        await self.handle_connection_code(
                            websocket, UnauthorizedException
                        )
                        continue
                    await self.handle_session_status_update(
                        websocket, session.id, user, packet.payload.get("status")
                    )

                else:
                    await self.handle_connection_code(
                        websocket, ActionNotImplementedException
                    )

        except WebSocketDisconnect:
            if manager.disconnect(session.id, websocket):
                await self.handle_session_message(
                    websocket, session.id, f"Client {user_id} left the session"
                )

    async def handle_session_status_update(
        self, websocket: WebSocket, session_id: int, user: User, status: str
    ):
        if not status in [e.value for e in SwipeSessionEnum]:
            await self.handle_connection_code(websocket, StatusNotFoundException)
            return

        await SwipeSessionService().update_swipe_session(
            UpdateSwipeSessionSchema(id=session_id, status=SwipeSessionEnum.COMPLETED),
            user,
        )

        payload = {"status": status}
        packet = PacketSchema(action=ACTIONS.SESSION_STATUS_UPDATE, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def handle_global_message(self, websocket: WebSocket, message: str) -> None:
        if not message:
            await self.handle_connection_code(websocket, NoMessageException)
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
            await self.handle_connection_code(websocket, NoMessageException)
            return

        payload = {"message": message}
        packet = PacketSchema(action=ACTIONS.SESSION_MESSAGE, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def handle_session_packet(
        self, session_id: int, packet: PacketSchema
    ) -> None:
        await manager.session_broadcast(session_id, packet)

    async def handle_connection_code(
        self, websocket, exception: CustomException | ConnectionCode
    ) -> None:
        payload = {"status_code": exception.code, "message": exception.message}
        packet = PacketSchema(action=ACTIONS.CONNECTION_CODE, payload=payload)

        await manager.personal_packet(websocket, packet)

    async def handle_recipe_swipe(
        self,
        websocket: WebSocket,
        session: SwipeSession,
        user: User,
        packet: PacketSchema,
    ) -> None:
        try:
            swipe_schema = CreateSwipeSchema(
                swipe_session_id=session.id, user_id=user.id, **packet.payload
            )

        except ValidationError as e:
            await self.handle_connection_code(websocket, ValidationException(e.json()))
            return

        recipe = await RecipeService().get_recipe_by_id(packet.payload["recipe_id"])
        if not recipe:
            await self.handle_connection_code(websocket, RecipeNotFoundException)
            return

        existing_swipe = await SwipeService().get_swipe_by_creds(
            swipe_session_id=session.id,
            user_id=user.id,
            recipe_id=packet.payload["recipe_id"],
        )

        if existing_swipe:
            await self.handle_connection_code(websocket, AlreadySwipedException)
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
                websocket, session.id, user, SwipeSessionEnum.COMPLETED
            )

    async def handle_session_match(
        self, websocket: WebSocket, session_id: int, recipe_id: int
    ) -> None:
        recipe = await RecipeService().get_recipe_by_id(recipe_id)
        if not recipe:
            await self.handle_connection_code(websocket, RecipeNotFoundException)
            return

        full_recipe = GetFullRecipeResponseSchema(**recipe.__dict__)

        payload = {"message": "A match has been found", "recipe": full_recipe}
        packet = PacketSchema(action=ACTIONS.RECIPE_MATCH, payload=payload)

        await self.handle_session_packet(session_id, packet)


manager = SwipeSessionConnectionManager()