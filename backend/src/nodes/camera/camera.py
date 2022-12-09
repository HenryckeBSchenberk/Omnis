from wswebcam.client import Camera
from .manager import Manager as CM
from api.websocket import ConnectionManager
from os import environ


class Camera_Websocket_API(ConnectionManager):
    def __init__(self, _id, camera):
        super().__init__(_id, camera)
        self.camera = self.interface
        self.valid_context = [
            'frame',
        ]

        self.valid_methods = [
            'get',
            'set',
            'help',
        ]

    async def get_help(self, websocket, data=None):
        await self.send_to(websocket, {
            'context': self.valid_context,
            'methods': self.valid_methods,
            'examples': [
                {'method': 'get', 'context': 'frame'},
                {'method': 'help', 'context': 'frame'},
                {'broadcast': 'True -> Will broadcast the status to all connected clients'}
            ]

        })
    
    def parser_finder(self, data):
        function = getattr(self, f"{data.get('method','').lower()}_{data.get('context','').lower()}", False)
        return function or self.get_help

    async def on_receive(self, websocket, data):
        function = self.parser_finder(data)

        try:
            async with self.camera:
                await function(websocket, data)

        except Exception as e:
            await self.send_to(websocket, {'error': str(e)})

        self.update_status(websocket, data)

    async def help_frame(self, websocket, data=None):
        response = {
            "frame": 'Base64 encoded image',
        }
        return await self.send_to(websocket, response)

    async def get_frame(self, websocket, data=None):
        await self.camera.read()
        await self.send_to(websocket, self.camera.data)

class CustomCamera(Camera):
    def __init__(self, host, port, manager=CM, loop=None, _id=None, name="Camera"):
        super().__init__(f"ws://{host}:{port}", loop=loop)
        self._id = _id
        self.name = name
        self._manager = manager
        self.webscoket_route = Camera_Websocket_API(self._id, self)
        self.data = None
        self._manager.add_device(self)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()