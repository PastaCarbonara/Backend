"""
Module for working with the websocket for the swipesessions.
"""

from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
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
from core.exceptions.websocket import (
    ActionNotImplementedException,
    AlreadySwipedException,
    ClosingConnection,
    StatusNotFoundException,
    SuccessfullConnection,
    ValidationException,
)
from core.db.enums import SwipeSessionActionEnum as ACTIONS, SwipeSessionEnum
from core.db.models import SwipeSession, User
from core.exceptions.base import CustomException, UnauthorizedException
from core.exceptions.recipe import RecipeNotFoundException
from core.helpers.hashid import decode_single
from core.helpers.websocket.auth import (
    IsActiveSession,
    IsAuthenticated,
    IsSessionMember,
)
from core.helpers.websocket.manager import WebsocketConnectionManager
from core.utils.token_helper import TokenHelper


manager = WebsocketConnectionManager(
    [[IsAuthenticated, IsSessionMember, IsActiveSession]]
)


class SwipeSessionWebsocketService:
    """
    This class provides a WebSocket service for communication between clients and servers using
    the WebSocket protocol.

    Attributes:
    -----------
    manager: WebSocketManager
        The manager responsible for handling WebSocket connections, disconnections, and message
        broadcasts
        in the WebSocket protocol.

    Methods:
    --------
    handler(websocket: WebSocket, session_id: str, user_id: int) -> None:
        This function is the WebSocket protocol's handler and takes a WebSocket instance as well
        as session and user IDs.

    handle_session_status_update(websocket: WebSocket, session_id: int, user: User, status: str)
    -> None:
        This function handles the updates on the session status and broadcasts the updates to all
        users in the session.

    handle_recipe_swipe(websocket: WebSocket, session: SwipeSession, user: User, packet:
    SwipeSessionPacketSchema) -> None:
        This function handles the creation of swipe requests to recipes in a session and
        broadcasts the request
        to all WebSocket clients in the same session.

    __init__(self, manager: WebSocketManager) -> None:
        Initializes the SwipeSessionWebsocketService instance with a manager that handles
        WebSocket connections,
        disconnections, and message broadcasts in the WebSocket protocol.

    handler(self, websocket: WebSocket, swipe_session_id: str, access_token: str) -> None:
        This function handles the WebSocket protocol and receives a WebSocket instance, swipe
        session ID, and
        the client's access token.

    get_user_and_swipe_session(self, access_token: str, swipe_session_id: str) -> Tuple[User,
    SwipeSession]:
        This function retrieves the user and swipe session associated with the given access
        token and swipe
        session ID.

    handle_global_message(self, packet: SwipeSessionPacketSchema, websocket: WebSocket, user:
    User, swipe_session: SwipeSession) -> None:
        This function handles a global message and ensures that the user is an administrator
        before broadcasting
        the message.

    handle_recipe_swipe(self, websocket: WebSocket, session: SwipeSession, user: User, packet:
    SwipeSessionPacketSchema) -> None:
        This function processes a recipe swipe and checks for a match with other participants
        in the swipe session.
    """

    def __init__(self) -> None:
        """
        Initializes the SwipeSessionWebsocketService instance with a WebSocketManager.

        Parameters:
        -----------
        manager: WebSocketManager
            The manager that handles the connection, disconnection and broadcasting of messages in
            WebSocket protocol.
        """
        self.manager = manager

        self.actions = {
            ACTIONS.GLOBAL_MESSAGE: self.handle_global_message,
            ACTIONS.RECIPE_SWIPE: self.handle_recipe_swipe,
            ACTIONS.POOL_MESSAGE: self.handle_pool_message,
            ACTIONS.SESSION_STATUS_UPDATE: self.handle_session_status_update,
        }

    async def handler(
        self, websocket: WebSocket, swipe_session_id: str, access_token: str
    ) -> None:
        """
        The handler function for WebSocket protocol, receives a WebSocket instance, the swipe
        session ID and client's access token.

        Parameters:
        -----------
        websocket: WebSocket
            The WebSocket instance.
        swipe_session_id: str
            The hashed swipe session ID.
        access_token: str
            The client's access token.

        Returns:
        --------
        None
        """
        exc = await self.manager.check_auth(
            access_token=access_token, swipe_session_id=swipe_session_id
        )
        if exc:
            await websocket.accept()
            await self.manager.handle_connection_code(websocket, exc)
            await websocket.close()
            return

        user, swipe_session = await self.get_user_and_swipe_session(
            access_token=access_token, swipe_session_id=swipe_session_id
        )

        await self.manager.connect(websocket, swipe_session.id)

        await self.manager.handle_connection_code(websocket, SuccessfullConnection)

        try:
            while websocket.application_state == WebSocketState.CONNECTED:
                try:
                    packet: SwipeSessionPacketSchema = await self.manager.receive_data(
                        websocket, SwipeSessionPacketSchema
                    )
                except CustomException as exc:
                    await self.manager.handle_connection_code(websocket, exc)
                    continue

                func = self.actions.get(
                    packet.action, self.handle_action_not_implemented
                )

                await func(
                    packet=packet,
                    websocket=websocket,
                    user=user,
                    swipe_session=swipe_session,
                )

        except WebSocketDisconnect:
            await self.manager.disconnect(websocket, swipe_session.id)

        except WebSocketException as exc:
            print("???")
            print(exc)

    async def get_user_and_swipe_session(
        self, access_token: str, swipe_session_id: str
    ) -> tuple[User, SwipeSession]:
        """Retrieve the user and swipe session associated with the given access token and swipe
        session ID.

        Args:
            access_token (str): The JWT access token used to authenticate the request.
            swipe_session_id (str): The ID of the swipe session to retrieve.

        Returns:
            Tuple[User, SwipeSession]: A tuple containing the User object associated with the access
            token, and the SwipeSession object associated with the given ID.

        Raises:
            InvalidTokenException: If the access token is invalid or has expired.
            NotFoundException: If the user or swipe session cannot be found.
        """
        decoded_token = TokenHelper.decode(token=access_token)
        user_id = decode_single(decoded_token.get("user_id"))
        swipe_session_id = decode_single(swipe_session_id)

        # By calling "check_auth" with "IsSessionMember", we already know that these exist
        user = await UserService().get_by_id(user_id)
        swipe_session = await SwipeSessionService().get_swipe_session_by_id(
            swipe_session_id
        )

        return (user, swipe_session)

    async def handle_global_message(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        swipe_session: SwipeSession,
    ):
        """
        Handle a global message sent by an admin user to all participants of a swipe session.

        Args:
            packet: A SwipeSessionPacketSchema object representing the packet containing the
                global message to handle.
            websocket: WebSocket object representing the active WebSocket connection.
            user: User object representing the user associated with the active WebSocket connection.
            swipe_session: not used

        Returns:
            None.
        """
        del swipe_session

        if not await UserService().is_admin(user.id):
            return await self.manager.handle_connection_code(
                websocket, UnauthorizedException
            )
        await self.manager.handle_global_message(
            websocket, packet.payload.get("message")
        )

    async def handle_recipe_swipe(
        self,
        websocket: WebSocket,
        swipe_session: SwipeSession,
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
                swipe_session_id=swipe_session.id, user_id=user.id, **packet.payload
            )

        except ValidationError as exc:
            await self.manager.handle_connection_code(
                websocket, ValidationException(exc.json())
            )
            return

        try:
            await RecipeService().get_recipe_by_id(packet.payload["recipe_id"])
        except RecipeNotFoundException:
            await self.manager.handle_connection_code(
                websocket, RecipeNotFoundException
            )
            return

        existing_swipe = await SwipeService().get_swipe_by_creds(
            swipe_session_id=swipe_session.id,
            user_id=user.id,
            recipe_id=packet.payload["recipe_id"],
        )

        if existing_swipe:
            await self.manager.handle_connection_code(websocket, AlreadySwipedException)
            return

        await SwipeService().create_swipe(swipe_schema)

        matching_swipes = (
            await SwipeService().get_swipes_by_session_id_and_recipe_id_and_like(
                swipe_session_id=swipe_session.id,
                recipe_id=packet.payload["recipe_id"],
                like=True,
            )
        )

        group = await GroupService().get_group_by_id(swipe_session.group_id)

        if len(matching_swipes) >= len(group.users):
            await self.handle_session_match(
                websocket, swipe_session.id, packet.payload["recipe_id"]
            )
            await self.handle_session_status_update(
                websocket, swipe_session.id, user, SwipeSessionEnum.COMPLETED
            )

            exception = ClosingConnection
            payload = {"status_code": exception.code, "message": exception.message}
            packet = SwipeSessionPacketSchema(
                action=ACTIONS.CONNECTION_CODE, payload=payload
            )

            await self.manager.disconnect_pool(swipe_session.id, packet)

    async def handle_pool_message(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        swipe_session: SwipeSession,
    ):
        """
        Handle a message sent by a participant of a swipe session to the session pool.

        Args:
            packet: A SwipeSessionPacketSchema object representing the packet containing the
            message to handle.
            websocket: WebSocket object representing the active WebSocket connection.
            user: not used
            swipe_session: A SwipeSession object representing the active swipe session.

        Returns:
            None.
        """
        del user

        await self.manager.handle_pool_message(
            websocket, swipe_session.id, packet.payload.get("message")
        )

    async def handle_session_status_update(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        swipe_session: SwipeSession,
    ):
        """
        Update the status of a swipe session and broadcast the change to all session participants.

        Args:
            packet: A SwipeSessionPacketSchema object representing the packet containing the new
            status of the swipe session to update.
            websocket: WebSocket object representing the active WebSocket connection.
            user: User object representing the user associated with the active WebSocket connection.
            swipe_session: A SwipeSession object representing the active swipe session.

        Returns:
            None.
        """
        if not await GroupService().is_admin(swipe_session.group_id, user.id):
            return await self.manager.handle_connection_code(
                websocket, UnauthorizedException
            )

        session_status = packet.payload.get("status")
        if not session_status in [e.value for e in SwipeSessionEnum]:
            return await self.manager.handle_connection_code(
                websocket, StatusNotFoundException
            )

        await SwipeSessionService().update_swipe_session(
            UpdateSwipeSessionSchema(
                id=swipe_session.id, status=SwipeSessionEnum.COMPLETED
            ),
            user,
        )

        payload = {"status": session_status}
        packet = SwipeSessionPacketSchema(
            action=ACTIONS.SESSION_STATUS_UPDATE, payload=payload
        )

        await self.manager.pool_broadcast(swipe_session.id, packet)

    async def handle_action_not_implemented(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        swipe_session: SwipeSession,
    ):
        """
        Handle an action packet that has not been implemented.

        Args:
            packet: not used
            websocket: WebSocket object representing the active WebSocket connection.
            user: not used
            swipe_session: not used

        Returns:
            None.
        """
        del packet, user, swipe_session

        await self.manager.handle_connection_code(
            websocket, ActionNotImplementedException
        )

    async def handle_session_match(
        self, websocket: WebSocket, session_id: int, recipe_id: int
    ) -> None:
        """
        Send a recipe match packet to all participants of a swipe session.

        Args:
            websocket (WebSocket): The WebSocket object representing the active WebSocket
            connection.
            session_id (int): An integer representing the ID of the swipe session to broadcast the
            packet to.
            recipe_id (int): An integer representing the ID of the recipe that was matched.

        Returns:
            None.
        """
        recipe = await RecipeService().get_recipe_by_id(recipe_id)
        if not recipe:
            await self.manager.handle_connection_code(
                websocket, RecipeNotFoundException
            )
            return

        print(recipe.__dict__)
        try:
            full_recipe = GetFullRecipeResponseSchema(**recipe.__dict__)
        except Exception as e:
            print(e)
            raise e
        payload = {"message": "A match has been found", "recipe": full_recipe}
        packet = SwipeSessionPacketSchema(action=ACTIONS.RECIPE_MATCH, payload=payload)

        await self.manager.pool_broadcast(session_id, packet)
