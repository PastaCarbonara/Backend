"""
Module for working with the websocket for the swipesessions.
"""

import json
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException # , status # 
from pydantic import ValidationError
from starlette.websockets import WebSocketState
from app.group.services.group import GroupService
from app.recipe.schemas.recipe import GetFullRecipeResponseSchema
from app.recipe.services.recipe import RecipeService
from app.swipe.schemas.swipe import CreateSwipeSchema
from app.swipe.services.swipe import SwipeService
from app.user.services.user import UserService
from app.swipe_session.schemas.swipe_session import (
    SwipeSessionPacketSchema,
    UpdateSwipeSessionSchema,
)
from app.swipe_session.services.swipe_session import SwipeSessionService
from core.exceptions.hashids import IncorrectHashIDException
from core.exceptions.websocket import (
    ActionNotFoundException,
    ActionNotImplementedException,
    AlreadySwipedException,
    ClosingConnection,
    InactiveException,
    InvalidIdException,
    JSONSerializableException,
    StatusNotFoundException,
    SuccessfullConnection,
    ValidationException,
)
from core.db.enums import SwipeSessionActionEnum as ACTIONS, SwipeSessionEnum
from core.db.models import SwipeSession, User
from core.exceptions.base import UnauthorizedException
from core.exceptions.recipe import RecipeNotFoundException
from core.helpers.hashid import check_id
from core.helpers.websocket_manager import WebsocketConnectionManager


manager = WebsocketConnectionManager()


class SwipeSessionWebsocketService:
    """
    WebSocket service for handling communication between client and server using WebSocket protocol.

    Attributes:
    -----------
    manager: WebSocketManager
        The manager that handles the connection, disconnection and broadcasting of messages in 
        WebSocket protocol.

    Methods:
    --------
    handler(websocket: WebSocket, session_id: str, user_id: int) -> None:
        The handler function for WebSocket protocol, receives a WebSocket instance and the session 
        and user IDs.

    handle_session_status_update(websocket: WebSocket, session_id: int, user: User, status: str) 
    -> None:
        Handles updates on the session status and broadcasts the update to all users in the session.

    handle_global_message(websocket: WebSocket, message: str) -> None:
        Handles the broadcasting of global messages to all WebSocket clients.

    handle_global_packet(packet: SwipeSessionPacketSchema) -> None:
        Handles the broadcasting of global packets to all WebSocket clients.

    handle_session_message(websocket: WebSocket, session_id: int, message: str) -> None:
        Handles the broadcasting of session messages to all WebSocket clients in the same session.

    handle_session_packet(session_id: int, packet: SwipeSessionPacketSchema) -> None:
        Handles the broadcasting of session packets to all WebSocket clients in the same session.

    handle_connection_code(websocket, exception: CustomException | ConnectionCode) -> None:
        Handles the creation of custom WebSocket packets containing the code and message of the 
        error.

    handle_recipe_swipe(websocket: WebSocket, session: SwipeSession, user: User, packet: 
    SwipeSessionPacketSchema) -> None:
        Handles the creation of swipe requests to recipes in a session and broadcasts the request 
        to all WebSocket clients in the same session.
    """
    def __init__(self) -> None:
        """
        Initializes the SwipeSessionWebsocketService instance.

        Parameters:
        -----------
        manager: WebSocketManager
            The manager that handles the connection, disconnection and broadcasting of messages in 
            WebSocket protocol.
        """
        self.manager = manager

    async def handler(
        self, websocket: WebSocket, session_id: str, user_id: int
    ) -> None:
        """
        The handler function for WebSocket protocol, receives a WebSocket instance and the session 
        and user IDs.

        Parameters:
        -----------
        websocket: WebSocket
            The WebSocket instance.
        session_id: str
            The session ID.
        user_id: int
            The user ID.

        Returns:
        --------
        None
        """
        try:
            user = await check_id(user_id, UserService().get_user_by_id)
            session = await check_id(
                session_id, SwipeSessionService().get_swipe_session_by_id
            )
        except IncorrectHashIDException:
            await self.manager.deny(websocket, InvalidIdException)
            return

        if session.status != SwipeSessionEnum.IN_PROGRESS:
            await self.manager.deny(websocket, InactiveException)
            return

        if session.group_id:
            if not await GroupService().is_member(session.group_id, user.id):
                await self.manager.deny(websocket, InvalidIdException)
                return

        websocket = await self.manager.connect(websocket, session.id)

        if not user or not session:
            await self.manager.handle_connection_code(websocket, InvalidIdException)
            await self.manager.disconnect(session.id, websocket)
            return

        await self.manager.handle_connection_code(websocket, SuccessfullConnection)

        try:
            while websocket.application_state == WebSocketState.CONNECTED:
                # NOTE! DO NOT 'RETURN' IF YOU WISH TO 'CONTINUE'
                # Learned it the hard way, and took me a day.

                data = await websocket.receive_text()

                # Gate keepers/Guard clauses
                try:
                    data_json = json.loads(data)
                except json.decoder.JSONDecodeError:
                    await self.manager.handle_connection_code(
                        websocket, JSONSerializableException
                    )
                    continue

                try:
                    packet = SwipeSessionPacketSchema(**data_json)
                except ValidationError:
                    await self.manager.handle_connection_code(
                        websocket, ActionNotFoundException
                    )
                    continue

                # Handlers
                if packet.action == ACTIONS.GLOBAL_MESSAGE:
                    if not await UserService().is_admin(user.id):
                        await self.manager.handle_connection_code(
                            websocket, UnauthorizedException
                        )
                        continue
                    await self.manager.handle_global_message(
                        websocket, packet.payload.get("message")
                    )

                elif packet.action == ACTIONS.RECIPE_SWIPE:
                    await self.handle_recipe_swipe(websocket, session, user, packet)

                elif packet.action == ACTIONS.POOL_MESSAGE:
                    await self.manager.handle_pool_message(
                        websocket, session.id, packet.payload.get("message")
                    )

                elif packet.action == ACTIONS.SESSION_STATUS_UPDATE:
                    if not await GroupService().is_admin(session.group_id, user.id):
                        await self.manager.handle_connection_code(
                            websocket, UnauthorizedException
                        )
                        continue
                    await self.handle_session_status_update(
                        websocket, session.id, user, packet.payload.get("status")
                    )

                else:
                    await self.manager.handle_connection_code(
                        websocket, ActionNotImplementedException
                    )

        except WebSocketDisconnect:
            await self.manager.disconnect(session.id, websocket)

        except WebSocketException as exc:
            print("???")
            print(exc)

    async def handle_session_status_update(
        self, websocket: WebSocket, session_id: int, user: User, session_status: str
    ):
        """
        Update the status of a swipe session and broadcast the change to all session participants.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            session_id: An integer representing the ID of the swipe session to update.
            user: User object representing the user associated with the active WebSocket connection.
            session_status: A string representing the new status of the swipe session.

        Returns:
            None.
        """
        if not session_status in [e.value for e in SwipeSessionEnum]:
            await self.manager.handle_connection_code(websocket, StatusNotFoundException)
            return

        # check is admin

        await SwipeSessionService().update_swipe_session(
            UpdateSwipeSessionSchema(id=session_id, status=SwipeSessionEnum.COMPLETED),
            user,
        )

        payload = {"status": session_status}
        packet = SwipeSessionPacketSchema(action=ACTIONS.SESSION_STATUS_UPDATE, payload=payload)

        await self.manager.pool_broadcast(session_id, packet)

    async def handle_recipe_swipe(
        self,
        websocket: WebSocket,
        session: SwipeSession,
        user: User,
        packet: SwipeSessionPacketSchema,
    ) -> None:
        """
        Process a recipe swipe and check for a match with other participants in the swipe session.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            session: A SwipeSession object representing the active swipe session.
            user: User object representing the user associated with the active WebSocket connection.
            packet: A SwipeSessionPacketSchema object representing the swipe packet to process.

        Returns:
            None.
        """
        try:
            swipe_schema = CreateSwipeSchema(
                swipe_session_id=session.id, user_id=user.id, **packet.payload
            )

        except ValidationError as exc:
            await self.manager.handle_connection_code(websocket, ValidationException(exc.json()))
            return

        try:
            await RecipeService().get_recipe_by_id(packet.payload["recipe_id"])
        except RecipeNotFoundException:
            await self.manager.handle_connection_code(websocket, RecipeNotFoundException)
            return

        existing_swipe = await SwipeService().get_swipe_by_creds(
            swipe_session_id=session.id,
            user_id=user.id,
            recipe_id=packet.payload["recipe_id"],
        )

        if existing_swipe:
            await self.manager.handle_connection_code(websocket, AlreadySwipedException)
            return

        await SwipeService().create_swipe(swipe_schema)

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

            exception = ClosingConnection
            payload = {"status_code": exception.code, "message": exception.message}
            packet = SwipeSessionPacketSchema(action=ACTIONS.CONNECTION_CODE, payload=payload)

            await self.manager.disconnect_pool(session.id, packet)

    async def handle_session_match(
        self, websocket: WebSocket, session_id: int, recipe_id: int
    ) -> None:
        """
        Send a recipe match packet to all participants of a swipe session.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            session_id: An integer representing the ID of the swipe session to broadcast the packet to.
            recipe_id: An integer representing the ID of the recipe that was matched.

        Returns:
            None.
        """
        recipe = await RecipeService().get_recipe_by_id(recipe_id)
        if not recipe:
            await self.manager.handle_connection_code(websocket, RecipeNotFoundException)
            return

        full_recipe = GetFullRecipeResponseSchema(**recipe.__dict__)

        payload = {"message": "A match has been found", "recipe": full_recipe}
        packet = SwipeSessionPacketSchema(action=ACTIONS.RECIPE_MATCH, payload=payload)

        await self.manager.pool_broadcast(session_id, packet)
