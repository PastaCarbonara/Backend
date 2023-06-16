"""
Module for working with the websocket for the swipesessions.
"""

from typing import Any, Coroutine
from fastapi import WebSocket
from pydantic import ValidationError
from app.group.services.group import GroupService
from app.recipe.exceptions.recipe import RecipeNotFoundException
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
from app.swipe_session_recipe_queue.services.swipe_session_recipe_queue import (
    SwipeSessionRecipeQueueService,
)
from core.db import session
from core.exceptions.websocket import (
    AlreadySwipedException,
    ClosingConnection,
    StatusNotFoundException,
    ValidationException,
)
from core.db.enums import SwipeSessionActionEnum, SwipeSessionEnum
from core.db.models import SwipeSession, User
from core.exceptions.base import UnauthorizedException
from core.helpers.hashid import decode_single
from core.helpers.websocket.auth import (
    IsActiveSession,
    IsAuthenticated,
    IsSessionMember,
)
from core.helpers.websocket.base import BaseWebsocketService
from core.helpers.websocket.manager import WebsocketConnectionManager
from core.utils.token_helper import TokenHelper


manager = WebsocketConnectionManager(
    [[IsAuthenticated, IsSessionMember, IsActiveSession]]
)


class SwipeSessionWebsocketService(BaseWebsocketService):
    """WebsocketService for SwipeSessions

    Attributes:
        - manager (WebsocketConnectionManager): Manage connections.
        - group_serv (GroupService): Deal with group functions.
        - swipe_session_serv (SwipeSessionService): Deal with swipe session functions.
        - swipe_serv (SwipeService): Deal with swipe functions.
        - recipe_serv (RecipeService): Deal with recipe functions.
        - queue_serv (SwipeSessionRecipeQueueService): Deal with queue functions.
        - user_serv (UserService): Deal with user functions.
        - actions (dict): Contains a map of actions.

    Methods:
        - __init__(): Initialize the service.

        - handler(websocket: WebSocket, swipe_session_id: int, access_token: str): Start
        the handler.

        - handle_get_recipes(packet: SwipeSessionPacketSchema, websocket: WebSocket,
        user: User, swipe_session: SwipeSession): Get recipes from the queue.

        - handle_global_message(packet: SwipeSessionPacketSchema, websocket: WebSocket,
        user: User, swipe_session: SwipeSession): Authorized version of
        handle_global_message.

        - handle_recipe_swipe(packet: SwipeSessionPacketSchema, websocket: WebSocket,
        user: User, swipe_session: SwipeSession): Process a swipe.

        - handle_session_status_update_auth(packet: SwipeSessionPacketSchema, websocket:
        WebSocket, user: User, swipe_session: SwipeSession): Authorized version of
        handle_session_status_update.

        - handle_session_status_update(packet: SwipeSessionPacketSchema, websocket:
        WebSocket, user: User, swipe_session: SwipeSession): Update the status of
        the SwipeSession.

        - handle_session_match(packet: SwipeSessionPacketSchema, websocket: WebSocket,
        user: User, swipe_session: SwipeSession): Process a swipe session recipe match.
    """

    def __init__(self) -> None:
        """Initialize the service."""
        self.group_serv = GroupService()
        self.swipe_session_serv = SwipeSessionService()
        self.swipe_serv = SwipeService()
        self.recipe_serv = RecipeService()
        self.queue_serv = SwipeSessionRecipeQueueService()
        self.user_serv = UserService()

        actions = {
            SwipeSessionActionEnum.GLOBAL_MESSAGE: self.handle_global_message,
            SwipeSessionActionEnum.RECIPE_SWIPE: self.handle_recipe_swipe,
            SwipeSessionActionEnum.POOL_MESSAGE: self.handle_pool_message,
            SwipeSessionActionEnum.SESSION_STATUS_UPDATE: self.handle_session_status_update_auth,  # noqa: E501
            SwipeSessionActionEnum.GET_RECIPES: self.handle_get_recipes,
        }

        super().__init__(
            manager=manager,
            actions=actions,
            schema=SwipeSessionPacketSchema,
        )

    async def handler(
        self,
        websocket: WebSocket,
        swipe_session_id: int,
        access_token: str,
    ) -> Coroutine[Any, Any, None]:
        """Initialize the handler with authentication.

        Args:
            websocket (WebSocket): The Websocket connection.
            swipe_session_id (int): Hashed SwipeSession id.
            access_token (str): JWT.

        Returns:
            Coroutine[Any, Any, None]: The handler loop.
        """
        exc = await self.manager.check_auth(
            access_token=access_token, swipe_session_id=swipe_session_id
        )
        if exc:
            await websocket.accept()
            await self.manager.handle_connection_code(websocket, exc)
            await websocket.close()
            return

        decoded_token = TokenHelper.decode(token=access_token)
        user_id = decode_single(decoded_token.get("user_id"))
        swipe_session_id = decode_single(swipe_session_id)

        # By calling "check_auth" with "IsSessionMember",
        # we already know that these exist
        user = await self.user_serv.get_by_id(user_id)
        swipe_session = await self.swipe_session_serv.get_swipe_session_by_id(
            swipe_session_id
        )

        return await super().handler(
            websocket=websocket,
            pool_id=swipe_session.id,
            user=user,
            swipe_session=swipe_session,
        )

    async def handle_get_recipes(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        swipe_session: SwipeSession,
        **kwargs
    ):
        """Function to get recipe's to the client using the QueueService."""
        del kwargs

        if packet.payload:
            limit = packet.payload.get("limit")
        else:
            limit = None

        print(limit)

        recipe_queue = await self.queue_serv.get_and_progress_queue(
            swipe_session.id, user.id, limit
        )

        if not recipe_queue and type(recipe_queue) is not list:
            await self.queue_serv.create_queue(swipe_session.id)
            recipe_queue = await self.queue_serv.get_and_progress_queue(
                swipe_session.id, user.id, limit
            )

        recipes = []
        for queue_item in recipe_queue:
            recipe = await self.recipe_serv.get_recipe_by_id(queue_item["recipe_id"])
            recipes.append(GetFullRecipeResponseSchema(**recipe.to_dict()))

        packet = SwipeSessionPacketSchema(
            action=SwipeSessionActionEnum.GET_RECIPES,
            payload={"recipes": recipes},
        )
        await self.manager.personal_packet(websocket, packet)

    async def handle_global_message(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        **kwargs
    ):
        """Handle a global message sent by an admin user to all participants of a
        swipe session.
        """
        del kwargs

        if not await self.user_serv.is_admin(user.id):
            return await self.manager.handle_connection_code(
                websocket, UnauthorizedException
            )

        await super().handle_global_message(packet=packet, websocket=websocket)

    async def handle_recipe_swipe(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        swipe_session: SwipeSession,
        **kwargs
    ) -> None:
        """Process a recipe swipe and check for a match with other participants in the
        swipe session.
        """
        del kwargs

        try:
            swipe_schema = CreateSwipeSchema(
                swipe_session_id=swipe_session.id, user_id=user.id, **packet.payload
            )
            recipe_id = packet.payload["recipe_id"]

        except ValidationError as exc:
            await self.manager.handle_connection_code(
                websocket, ValidationException(exc.json())
            )
            return

        try:
            await self.recipe_serv.get_recipe_by_id(recipe_id)
        except RecipeNotFoundException:
            await self.manager.handle_connection_code(
                websocket, RecipeNotFoundException
            )
            return

        existing_swipe = await self.swipe_serv.get_swipe_by_creds(
            swipe_session_id=swipe_session.id,
            user_id=user.id,
            recipe_id=recipe_id,
        )

        if existing_swipe:
            await self.manager.handle_connection_code(websocket, AlreadySwipedException)
            return

        await self.swipe_serv.create_swipe(swipe_schema)
        if packet.payload["like"]:
            await self.queue_serv.add_to_queue(swipe_session.id, recipe_id)

        matching_swipes = (
            await self.swipe_serv.get_swipes_by_session_id_and_recipe_id_and_like(
                swipe_session_id=swipe_session.id,
                recipe_id=recipe_id,
                like=True,
            )
        )
        print(matching_swipes)

        group = await self.group_serv.get_group_by_id(swipe_session.group_id)
        print(group.users)

        if len(matching_swipes) >= len(group.users):
            await self.handle_session_match(websocket, swipe_session, recipe_id)

            packet = SwipeSessionPacketSchema(
                action=SwipeSessionActionEnum.SESSION_STATUS_UPDATE,
                payload={"status": SwipeSessionEnum.COMPLETED},
            )
            await self.handle_session_status_update(
                packet, websocket, swipe_session
            )

            exception = ClosingConnection
            payload = {"status_code": exception.code, "message": exception.message}
            packet = SwipeSessionPacketSchema(
                action=SwipeSessionActionEnum.CONNECTION_CODE, payload=payload
            )
            await self.manager.disconnect_pool(swipe_session.id, packet)

    async def handle_session_status_update_auth(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        user: User,
        swipe_session: SwipeSession,
        **kwargs
    ):
        """Authorized version of handle_session_status_update."""
        del kwargs

        if not await self.group_serv.is_admin(swipe_session.group_id, user.id):
            await self.manager.handle_connection_code(websocket, UnauthorizedException)
            return

        return await self.handle_session_status_update(
            packet, websocket, swipe_session
        )

    async def handle_session_status_update(
        self,
        packet: SwipeSessionPacketSchema,
        websocket: WebSocket,
        swipe_session: SwipeSession,
        **kwargs
    ):
        """Update the status of a swipe session and broadcast the change to all session
        participants.
        """
        del kwargs

        session_status = packet.payload.get("status")
        if session_status not in [e.value for e in SwipeSessionEnum]:
            return await self.manager.handle_connection_code(
                websocket, StatusNotFoundException
            )

        await self.swipe_session_serv.update_swipe_session(
            UpdateSwipeSessionSchema(id=swipe_session.id, status=session_status),
            swipe_session.group_id,
        )

        payload = {"status": session_status}
        packet = SwipeSessionPacketSchema(
            action=SwipeSessionActionEnum.SESSION_STATUS_UPDATE, payload=payload
        )

        return await self.manager.pool_broadcast(swipe_session.id, packet)

    async def handle_session_match(
        self,
        websocket: WebSocket,
        swipe_session: SwipeSession,
        recipe_id: int,
        **kwargs
    ) -> None:
        """Send a recipe match packet to all participants of a swipe session."""
        del kwargs

        recipe = await self.recipe_serv.get_recipe_by_id(recipe_id)
        if not recipe:
            await self.manager.handle_connection_code(
                websocket, RecipeNotFoundException
            )
            return

        swipe_session.swipe_match = recipe
        await session.commit()

        full_recipe = GetFullRecipeResponseSchema(**recipe.to_dict())

        payload = {"message": "A match has been found", "recipe": full_recipe}
        packet = SwipeSessionPacketSchema(
            action=SwipeSessionActionEnum.RECIPE_MATCH, payload=payload
        )

        await self.manager.pool_broadcast(swipe_session.id, packet)
