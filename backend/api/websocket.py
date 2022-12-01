from asyncio import sleep
from uuid import uuid4

from starlette.endpoints import WebSocketEndpoint

class ConnectionManager(WebSocketEndpoint):
    encoding = "json"

    def __init__(self, _id, interface):
        self._id = _id or uuid4().hex
        self.connections = []
        self.interface = interface

    def __call__(self, scope, receive, send):
        super().__init__(scope, receive, send)
        return self

    async def on_connect(self, websocket):
        await websocket.accept()
        self.connections.append(websocket)
        await sleep(0.5)

    async def on_receive(self, websocket, data=None):
        await websocket.send_json({"echo": data})

    async def on_disconnect(self, websocket, *args):
        self.connections.remove(websocket)

    async def send_to(self, websocket, payload: dict):
        await websocket.send_json(payload)

    async def broadcast(self, payload: dict):
        for client in self.connections:
            await self.send_to(client, payload)
