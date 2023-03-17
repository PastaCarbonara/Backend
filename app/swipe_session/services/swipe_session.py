import enum
from fastapi import WebSocket, WebSocketDisconnect


class SwipeSessionConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()

        # Check if session_id exists in db

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        self.active_connections[session_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, session_id: str, message: str):

        # store message?

        for connection in self.active_connections[session_id]:
            await connection.send_text(message)


class SwipeSessionService:
    def __init__(self) -> None:
        ...

    async def handler(self, websocket: WebSocket, session_id: str, client_id: int):
        await manager.connect(websocket, session_id)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.send_personal_message(f"You wrote: {data}", websocket)
                await manager.broadcast(session_id, data)

        except WebSocketDisconnect:
            manager.disconnect(session_id, websocket)
            await manager.broadcast(session_id, '{"message": f"Client '+str(client_id)+' left the chat"}')


manager = SwipeSessionConnectionManager()
