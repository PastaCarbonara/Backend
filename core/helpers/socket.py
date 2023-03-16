import asyncio
from collections import defaultdict
import json
from typing import List
from fastapi import WebSocket
from core.helpers.redis import redis as rds

class ConnectionManager:
    def __init__(self):
        self.active_connections = defaultdict(dict)

    async def connect(self, websocket: WebSocket, application: str, client_id: str):
        await websocket.accept()
        if application not in self.active_connections:
            self.active_connections[application] = defaultdict(list)

        self.active_connections[application][client_id].append(websocket)

    def disconnect(self, websocket: WebSocket, application: str, client_id: str):
        self.active_connections[application][client_id].remove(websocket)

    async def broadcast(self, message: dict, application: str, client_id: str):
        for connection in self.active_connections[application][client_id]:
            try:
                await connection.send_json(message)
                print(f"sent {message}")
            except Exception as e:
                pass

    async def consume(self):
        print("started to consume")
        sub = rds.pubsub()
        sub.subscribe('channel')
        while True:
            await asyncio.sleep(0.01)
            message = sub.get_message(ignore_subscribe_messages=True)
            if message is not None and isinstance(message, dict):
                msg = json.loads(message.get('data'))
                await self.broadcast(msg['message'], msg['application'], msg['client_id'])


manager = ConnectionManager()