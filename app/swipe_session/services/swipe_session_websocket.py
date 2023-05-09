"""
Module for working with the websocket for the swipesessions.
"""

import json
from fastapi import WebSocket, WebSocketDisconnect, status # WebSocketException
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
    ClosingConnection,
    ConnectionCode,
    InactiveException,
    InvalidIdException,
    JSONSerializableException,
    NoMessageException,
    StatusNotFoundException,
    SuccessfullConnection,
    ValidationException,
)
from starlette.websockets import WebSocketState
from app.user.services.user import UserService
from app.swipe_session.schemas.swipe_session import (
    PacketSchema,
    UpdateSwipeSessionSchema,
)
from app.swipe_session.services.swipe_session import SwipeSessionService
from core.db.enums import SwipeSessionActionEnum as ACTIONS, SwipeSessionEnum
from core.db.models import SwipeSession, User
from core.exceptions.base import CustomException, UnauthorizedException
from core.exceptions.recipe import RecipeNotFoundException
from core.helpers.hashid import check_id


class SwipeSessionConnectionManager:
    """
    Manages WebSocket connections for SwipeSession.

    Maintains active connections for each session ID, and provides methods 
    to connect, disconnect, and send packets to clients. Also provides 
    methods to get information about active connections.
    """
    def __init__(self):
        """
        Initializes SwipeSessionConnectionManager with an empty dictionary to hold active 
        connections.
        """
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """
        Accepts a WebSocket connection and adds it to the active connections list for a given 
        session ID.

        Args:
            websocket (WebSocket): The WebSocket connection to add to the active connections list.
            session_id (str): The ID of the session to which the connection belongs.

        Returns:
            WebSocket: The WebSocket connection that was added to the active connections list.
        """
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

        return websocket

    async def deny(
        self, websocket: WebSocket, exception: CustomException = AccessDeniedException
    ) -> None:
        """
        Denies access to a WebSocket connection and closes the connection with a custom exception.

        Args:
            websocket (WebSocket): The WebSocket connection to deny access to.
            exception (CustomException): The exception to raise to indicate the reason 
            for the access denial.
        """
        await websocket.accept()
        await SwipeSessionWebsocketService().handle_connection_code(
            websocket, exception
        )
        await websocket.close(status.WS_1000_NORMAL_CLOSURE)

    async def disconnect(self, session_id: str, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active connections list for a given session ID.

        If the active connections list for the session ID becomes empty, removes the session ID 
        from the active connections dictionary.

        Args:
            session_id (str): The ID of the session from which to remove the WebSocket connection.
            websocket (WebSocket): The WebSocket connection to remove from the active connections list.
        """
        self.active_connections[session_id].remove(websocket)
        await websocket.close()

        if self.get_connection_count(session_id) < 1:
            self.active_connections.pop(session_id)

        # pain.
        # else:
        #     await self.handle_session_message(
        #         websocket, session_id, f"Client left the session"
        #     )

    async def disconnect_session(self, session_id, packet) -> None:
        """
        Sends a packet to all WebSocket connections in a given session ID and removes each connection from the active
        connections list.

        Args:
            session_id (str): The ID of the session from which to disconnect all WebSocket connections.
            packet (PacketSchema): The packet to send to all WebSocket connections before disconnecting.
        """
        session = self.active_connections.get(session_id)

        if not session:  # Error Log this
            print("Tried to disconnect for non existing session")
            return

        websocket: WebSocket
        for websocket in session:
            await self.personal_packet(websocket, packet)
            await self.disconnect(session_id, websocket)

    async def personal_packet(self, websocket: WebSocket, packet: PacketSchema) -> None:
        """
        Sends a packet to a single WebSocket connection.

        Args:
            websocket (WebSocket): The WebSocket connection to send the packet to.
            packet (PacketSchema): The packet to send.
        """
        await websocket.send_json(packet.dict())

    async def global_broadcast(self, packet: PacketSchema) -> None:
        """Broadcasts a packet to all connected websockets across all sessions.

        Args:
            packet (PacketSchema): The packet to be broadcasted.
        """
        for session_id in self.active_connections.keys():
            for connection in self.active_connections[session_id]:
                await connection.send_json(packet.dict())

    async def session_broadcast(self, session_id: str, packet: PacketSchema) -> None:
        """Broadcasts a packet to all websockets connected to a specific session.

        Args:
            session_id (str): The ID of the session to broadcast to.
            packet (PacketSchema): The packet to be broadcasted.
        """
        for connection in self.active_connections[session_id]:
            await connection.send_json(packet.dict())

    def get_connection_count(self, session_id: str | None = None) -> int:
        """"Gets the total number of active websocket connections across all sessions, or the number of
        connections for a specific session if session_id is provided.

        Args:
            session_id (str | None, optional): The ID of the session to get connection count for.
                Defaults to None.

        Returns:
            int: The total number of active websocket connections.
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


manager = SwipeSessionConnectionManager()


class SwipeSessionWebsocketService:
    """
    WebSocket service for handling communication between client and server using WebSocket protocol.

    Attributes:
    -----------
    manager: WebSocketManager
        The manager that handles the connection, disconnection and broadcasting of messages in WebSocket protocol.

    Methods:
    --------
    handler(websocket: WebSocket, session_id: str, user_id: int) -> None:
        The handler function for WebSocket protocol, receives a WebSocket instance and the session and user IDs.

    handle_session_status_update(websocket: WebSocket, session_id: int, user: User, status: str) -> None:
        Handles updates on the session status and broadcasts the update to all users in the session.

    handle_global_message(websocket: WebSocket, message: str) -> None:
        Handles the broadcasting of global messages to all WebSocket clients.

    handle_global_packet(packet: PacketSchema) -> None:
        Handles the broadcasting of global packets to all WebSocket clients.

    handle_session_message(websocket: WebSocket, session_id: int, message: str) -> None:
        Handles the broadcasting of session messages to all WebSocket clients in the same session.

    handle_session_packet(session_id: int, packet: PacketSchema) -> None:
        Handles the broadcasting of session packets to all WebSocket clients in the same session.

    handle_connection_code(websocket, exception: CustomException | ConnectionCode) -> None:
        Handles the creation of custom WebSocket packets containing the code and message of the error.

    handle_recipe_swipe(websocket: WebSocket, session: SwipeSession, user: User, packet: PacketSchema) -> None:
        Handles the creation of swipe requests to recipes in a session and broadcasts the request to all WebSocket clients in the same session.
    """
    def __init__(self) -> None:
        """
        Initializes the SwipeSessionWebsocketService instance.

        Parameters:
        -----------
        manager: WebSocketManager
            The manager that handles the connection, disconnection and broadcasting of messages in WebSocket protocol.
        """
        self.manager = manager

    async def handler(
        self, websocket: WebSocket, session_id: str, user_id: int
    ) -> None:
        """
        The handler function for WebSocket protocol, receives a WebSocket instance and the session and user IDs.

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
        except Exception:
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
            await self.handle_connection_code(websocket, InvalidIdException)
            await self.manager.disconnect(session.id, websocket)
            return

        await self.handle_connection_code(websocket, SuccessfullConnection)

        try:
            while websocket.application_state == WebSocketState.CONNECTED:
                # NOTE! DO NOT 'RETURN' IF YOU WISH TO 'CONTINUE'
                # Learned it the hard way, and took me a day.

                data = await websocket.receive_text()

                # Gate keepers/Guard clauses
                try:
                    data_json = json.loads(data)
                except Exception:
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
            await self.manager.disconnect(session.id, websocket)

        except Exception as exc:
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
            await self.handle_connection_code(websocket, StatusNotFoundException)
            return

        # check is admin

        await SwipeSessionService().update_swipe_session(
            UpdateSwipeSessionSchema(id=session_id, status=SwipeSessionEnum.COMPLETED),
            user,
        )

        payload = {"status": session_status}
        packet = PacketSchema(action=ACTIONS.SESSION_STATUS_UPDATE, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def handle_global_message(self, websocket: WebSocket, message: str) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            message: A string representing the message to broadcast.

        Returns:
            None.
        """
        if not message:
            await self.handle_connection_code(websocket, NoMessageException)
            return

        payload = {"message": message}
        packet = PacketSchema(action=ACTIONS.GLOBAL_MESSAGE, payload=payload)

        await self.handle_global_packet(packet)

    async def handle_global_packet(self, packet: PacketSchema) -> None:
        """
        Broadcast a packet to all connected clients.

        Args:
            packet: A PacketSchema object representing the packet to broadcast.

        Returns:
            None.
        """
        await self.manager.global_broadcast(packet)

    async def handle_session_message(
        self, websocket: WebSocket, session_id: int, message: str
    ) -> None:
        """
        Broadcast a message to all participants of a swipe session.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            session_id: An integer representing the ID of the swipe session to broadcast the message to.
            message: A string representing the message to broadcast.

        Returns:
            None.
        """
        if not message:
            await self.handle_connection_code(websocket, NoMessageException)
            return

        payload = {"message": message}
        packet = PacketSchema(action=ACTIONS.SESSION_MESSAGE, payload=payload)

        await self.handle_session_packet(session_id, packet)

    async def handle_session_packet(
        self, session_id: int, packet: PacketSchema
    ) -> None:
        """
        Broadcast a packet to all participants of a swipe session.

        Args:
            session_id: An integer representing the ID of the swipe session to broadcast the packet to.
            packet: A PacketSchema object representing the packet to broadcast.

        Returns:
            None.
        """
        await self.manager.session_broadcast(session_id, packet)

    async def handle_connection_code(
        self, websocket, exception: CustomException | ConnectionCode
    ) -> None:
        """
        Send a custom connection code packet to the client.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            exception: A CustomException or ConnectionCode object representing the error to report to the client.

        Returns:
            None.
        """
        payload = {"status_code": exception.code, "message": exception.message}
        packet = PacketSchema(action=ACTIONS.CONNECTION_CODE, payload=payload)

        await self.manager.personal_packet(websocket, packet)

    async def handle_recipe_swipe(
        self,
        websocket: WebSocket,
        session: SwipeSession,
        user: User,
        packet: PacketSchema,
    ) -> None:
        """
        Process a recipe swipe and check for a match with other participants in the swipe session.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            session: A SwipeSession object representing the active swipe session.
            user: User object representing the user associated with the active WebSocket connection.
            packet: A PacketSchema object representing the swipe packet to process.

        Returns:
            None.
        """
        try:
            swipe_schema = CreateSwipeSchema(
                swipe_session_id=session.id, user_id=user.id, **packet.payload
            )

        except ValidationError as e:
            await self.handle_connection_code(websocket, ValidationException(e.json()))
            return

        try:
            await RecipeService().get_recipe_by_id(packet.payload["recipe_id"])
        except Exception:
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
            packet = PacketSchema(action=ACTIONS.CONNECTION_CODE, payload=payload)

            await self.manager.disconnect_session(session.id, packet)

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
            await self.handle_connection_code(websocket, RecipeNotFoundException)
            return

        full_recipe = GetFullRecipeResponseSchema(**recipe.__dict__)

        payload = {"message": "A match has been found", "recipe": full_recipe}
        packet = PacketSchema(action=ACTIONS.RECIPE_MATCH, payload=payload)

        await self.handle_session_packet(session_id, packet)
