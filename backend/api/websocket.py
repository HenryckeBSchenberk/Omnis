from asyncio import sleep
from bson import ObjectId as new_id


from starlette.endpoints import WebSocketEndpoint

class ConnectionManager(WebSocketEndpoint):
    encoding = "json"

    def __init__(self, _id=None, interface=None):
        self._id = new_id(_id)
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
        raise NotImplementedError
    
    async def update_status(self, websocket, data={}):
        if data.get('broadcast'):
            return await self.broadcast(self.interface.update_status())
        else:
            return await self.send_to(websocket, self.interface.update_status())

    async def on_disconnect(self, websocket, *args):
        self.connections.remove(websocket)

    async def send_to(self, websocket, payload: dict):
        await websocket.send_json(payload)

    async def broadcast(self, payload: dict):
        for client in self.connections:
            await self.send_to(client, payload)
