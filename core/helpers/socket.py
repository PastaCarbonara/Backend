import asyncio
from collections import defaultdict
import json
import time
from typing import List
from fastapi import WebSocket
from core.helpers.redis import redis as rds


class Packet:
    def __init__(self) -> None:
        id = round(time.time() * 1000)
        payload = {}

    def json(self):
        return json.dumps(self.__dict__)

class SwipeSessionConnectionManager:
    def __init__(self):
        self.active_connections: dict = defaultdict(dict)

    async def connect(self, websocket: WebSocket, application: str):
        await websocket.accept()
        if application not in self.active_connections:
            print(f"new application: {application}")
            self.active_connections[application]: List[WebSocket] = []

        self.active_connections[application].append(websocket)

    def disconnect(self, websocket: WebSocket, application: str):
        self.active_connections[application].remove(websocket)

        if len(self.active_connections[application]) == 0:
            self.active_connections.pop(application)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, application: str):
        for connection in self.active_connections[application]:
            print(f"Broadcasting '{message}'")
            await connection.send_text(message)
    # def __init__(self):
    #     self.active_connections = defaultdict(dict)

    # async def connect(self, websocket: WebSocket, application: str, client_id: str):
    #     await websocket.accept()
    #     if application not in self.active_connections:
    #         print(f"new application: {application}")
    #         self.active_connections[application] = defaultdict(list)

    #     self.active_connections[application].append(websocket)

    # def disconnect(self, websocket: WebSocket, application: str, client_id: str):
    #     self.active_connections[application][client_id].remove(websocket)

    # async def broadcast(self, message: str, application: str, client_id: str):
    #     for app_connections in self.active_connections[application]:
    #         for connection in app_connections:
    #             try:
    #                 await connection.send_json(message)
    #                 print(f"{client_id} sent {message}")
    #             except Exception as e:
    #                 print(f"failed: {application}:{client_id}:{message}")
    #                 pass


manager = SwipeSessionConnectionManager()