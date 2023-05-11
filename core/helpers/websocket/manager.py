"""
Connection manager for websockets
"""

import json
from fastapi import WebSocket, status
from pydantic import ValidationError
from pydantic.main import ModelMetaclass
from core.db.enums import WebsocketActionEnum
from core.exceptions.base import CustomException
from core.exceptions.websocket import (
    AccessDeniedException,
    ActionNotFoundException,
    ConnectionCode,
    JSONSerializableException,
    NoMessageException,
)
from core.helpers.schemas.websocket import WebsocketPacketSchema


class WebsocketConnectionManager:
    """
    Manages WebSocket connections.

    Maintains active connections for each pool ID, and provides methods
    to connect, disconnect, and send packets to clients. Also provides
    methods to get information about active pools of connections.
    """

    def __init__(self):
        """
        Initializes WebsocketConnectionManager with an empty dictionary to hold active
        pools and its connections.
        """
        self.active_pools: dict = {}

    async def connect(self, websocket: WebSocket, pool_id: str) -> None:
        """
        Accepts a WebSocket connection and adds it to the active pools list for a given pool ID.

        Args:
            websocket (WebSocket): The WebSocket connection to add to the active pools list.
            pool_id (str): The ID of the pool to which the connection belongs.

        Returns:
            WebSocket: The WebSocket connection that was added to the active pools list.
        """
        await websocket.accept()

        if pool_id not in self.active_pools:
            self.active_pools[pool_id] = []

        self.active_pools[pool_id].append(websocket)

        return websocket

    async def receive_data(self, websocket: WebSocket, schema: ModelMetaclass):
        """
        Receives and validates data from the given websocket.

        Args:
            websocket (WebSocket): The websocket to receive data from.
            schema (ModelMetaclass): The schema to validate the received data.

        Returns:
            Any: The deserialized and validated data packet.

        Raises:
            JSONSerializableException: If the received data cannot be decoded to a JSON object.
            ActionNotFoundException: If the received data fails to validate against the given schema.
        """
        data = await websocket.receive_text()

        try:
            data_json = json.loads(data)
        except json.decoder.JSONDecodeError as exc:
            raise JSONSerializableException from exc

        try:
            packet = schema(**data_json)
        except ValidationError as exc:
            raise ActionNotFoundException from exc

        return packet

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
        await self.handle_connection_code(websocket, exception)
        await websocket.close(status.WS_1000_NORMAL_CLOSURE)

    async def disconnect(self, pool_id: str, websocket: WebSocket):
        """
        Removes a WebSocket connection from the active pools list for a given pool ID.

        If the active pools list for the pool ID becomes empty, removes the pool ID
        from the active pools dictionary.

        Args:
            pool_id (str): The ID of the pool from which to remove the WebSocket connection.
            websocket (WebSocket): The WebSocket connection to remove from the active
            pools list.
        """
        self.active_pools[pool_id].remove(websocket)
        await websocket.close()

        if self.get_connection_count(pool_id) < 1:
            self.active_pools.pop(pool_id)

        # pain.
        # else:
        #     await self.handle_pool_message(
        #         websocket, pool_id, f"Client left the pool"
        #     )

    async def disconnect_pool(self, pool_id, packet) -> None:
        """
        Sends a packet to all WebSocket connections in a given pool and removes each connection
        from the active pools list.

        Args:
            pool_id (str): The ID of the pool from which to disconnect all WebSocket connections.
            packet (WebsocketPacketSchema): The packet to send to all WebSocket connections before
            disconnecting.
        """
        pool = self.active_pools.get(pool_id)

        if not pool:  # Error Log this
            print("Tried to disconnect for non existing pool")
            return

        websocket: WebSocket
        for websocket in pool:
            await self.personal_packet(websocket, packet)
            await self.disconnect(pool_id, websocket)

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
        packet = WebsocketPacketSchema(
            action=WebsocketActionEnum.GLOBAL_MESSAGE, payload=payload
        )

        await self.global_broadcast(packet)

    async def handle_pool_message(
        self, websocket: WebSocket, pool_id: int, message: str
    ) -> None:
        """
        Broadcast a message to all participants of a pool.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            pool_id: An integer representing the ID of the pool to broadcast
            the message to.
            message: A string representing the message to broadcast.

        Returns:
            None.
        """
        if not message:
            await self.handle_connection_code(websocket, NoMessageException)
            return

        payload = {"message": message}
        packet = WebsocketPacketSchema(
            action=WebsocketActionEnum.POOL_MESSAGE, payload=payload
        )

        await self.pool_broadcast(pool_id, packet)

    async def handle_connection_code(
        self, websocket, exception: CustomException | ConnectionCode
    ) -> None:
        """
        Send a custom connection code packet to the client.

        Args:
            websocket: WebSocket object representing the active WebSocket connection.
            exception: A CustomException or ConnectionCode object representing the error to
            report to the client.

        Returns:
            None.
        """
        payload = {"status_code": exception.code, "message": exception.message}
        packet = WebsocketPacketSchema(
            action=WebsocketActionEnum.CONNECTION_CODE, payload=payload
        )

        await self.personal_packet(websocket, packet)

    async def personal_packet(
        self, websocket: WebSocket, packet: WebsocketPacketSchema
    ) -> None:
        """
        Sends a packet to a single WebSocket connection.

        Args:
            websocket (WebSocket): The WebSocket connection to send the packet to.
            packet (WebsocketPacketSchema): The packet to send.
        """
        await websocket.send_json(packet.dict())

    async def global_broadcast(self, packet: WebsocketPacketSchema) -> None:
        """Broadcasts a packet to all connected websockets across all pools.

        Args:
            packet (WebsocketPacketSchema): The packet to be broadcasted.
        """
        for _, connections in self.active_pools.items():
            for connection in connections:
                await connection.send_json(packet.dict())

    async def pool_broadcast(self, pool_id: str, packet: WebsocketPacketSchema) -> None:
        """Broadcasts a packet to all websockets connected to a specific pool.

        Args:
            pool_id (str): The ID of the pool to broadcast to.
            packet (WebsocketPacketSchema): The packet to be broadcasted.
        """
        for connection in self.active_pools[pool_id]:
            await connection.send_json(packet.dict())

    def get_connection_count(self, pool_id: str | None = None) -> int:
        """ "Gets the total number of active websocket connections across all pools, or the number of
        connections for a specific pool if pool_id is provided.

        Args:
            pool_id (str | None, optional): The ID of the pool to get connection count for.
                Defaults to None.

        Returns:
            int: The total number of active websocket connections.
        """
        if pool_id:
            try:
                connections = self.active_pools[pool_id]
            except KeyError:
                # Perhaps a better way to resolve this exists, as this might be unclear
                return 0

            return len(connections)

        total = 0
        for _, connections in self.active_pools.items():
            total += len(connections)

        return total