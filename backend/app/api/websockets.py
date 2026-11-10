import json
from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websockets"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]):
        # Send to all connected clients
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # If a connection dies, clean it up
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection open. We don't expect messages from the client.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)