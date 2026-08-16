import json
from typing import Dict, List
from fastapi import WebSocket
from app.core.redis import redis_client

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, role: str):
        await websocket.accept()
        if role not in self.active_connections:
            self.active_connections[role] = []
        self.active_connections[role].append(websocket)

    def disconnect(self, websocket: WebSocket, role: str):
        if role in self.active_connections:
            self.active_connections[role].remove(websocket)

    async def broadcast_to_role(self, role: str, message: dict):
        if role in self.active_connections:
            for connection in self.active_connections[role]:
                await connection.send_json(message)

    async def publish_redis_event(self, channel: str, message: dict):
        await redis_client.publish(channel, json.dumps(message))

    async def listen_to_redis(self):
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("campus_alerts", "complaint_updates")
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                target_role = data.get("target_role", "STUDENT")
                await self.broadcast_to_role(target_role, data)

ws_manager = ConnectionManager()
