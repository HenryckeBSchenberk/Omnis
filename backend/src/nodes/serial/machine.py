from asyncio import sleep, wait_for
from api.websocket import ConnectionManager
from uuid import uuid4
from .gcode import GCODE
class Machine_Websocket_API(ConnectionManager):
    def __init__(self, _id, machine):
        super().__init__(_id, machine)
        self.machine = self.interface
        self.valid_context = [
            'position',
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
                {'method': 'get', 'context': 'position'},
                {'method': 'set', 'context': 'position', 'axis': {'X': 100, 'Y': 150}, 'relative': True, 'wait': True, 'broadcast': True},
                {'method': 'help', 'context': 'position'}
            ]

        })

    async def help_position(self, websocket, data=None):
        return await self.send_to(websocket, {
                'axis': "{Axis_Name:Desired_Position} | {X:100, Y:150, Z:..., ...}",
                'relative': '(True/Flase) -> G91 | G90',
                'wait': '(True/Flase) -> Will block until the machine has reached the desired position',
                'broadcast': '(True/Flase) -> Will broadcast the new position to all connected clients',
            })

    def parser_finder(self, data):
        function = getattr(self, f"{data.get('method','').lower()}_{data.get('context','').lower()}", False)
        return function or self.get_help

    async def set_position(self, websocket, data):
        if data.get('relative'):
            await self.machine.set_relative()

        if not data.get('wait'):
            await self.machine.set_position(data.get('axis'))
        else:
            await self.machine.set_position_and_wait(data.get('axis'))

        if not self.machine.absolute:
            await self.machine.set_absolute()

    async def get_position(self, websocket, data=None):
        position = await self.machine.get_position()
        await self.send_to(websocket, position)

    async def on_receive(self, websocket, data):
        function = self.parser_finder(data)
        try:
            async with self.machine.parser:
                await function(websocket, data)
                self.machine.clear_errors()
                status = self.machine.update_status()
        except Exception as e:
            await self.send_to(websocket, {'error': str(e)})
            self.machine.set_error(e)
            status = self.machine.update_status()

        if data.get('broadcast'):
            return await self.broadcast(status)
        return await self.send_to(websocket, status)


class Machine:
    def __init__(self, parser, axis=None, pins=None, _id=None) -> None:
        self._id = _id or uuid4().hex
        self.axis = axis
        self.pins = pins
        self.parser = parser
        self.__last_position = {}
        self.absolute = True
        self.webscoket_route = Machine_Websocket_API(self._id, self)
        self.parser._manager.add_device(self)
        self.whiout_error = True

    def if_helethy(func):
        async def wrapper(self, *args, **kwargs):
            if self.helthly:
                return await func(self, *args, **kwargs)
        return wrapper

    def clear_errors(self):
        self.whiout_error = True

    def set_error(self, error):
        self.whiout_error = False
        self.last_error = error

   
    async def __aenter__(self):
        await self.parser.connect()
        return self

    async def __aexit__(self, *args):
        await self.parser.websocket.close() #! Update wspyserial to provide .disconnect() insted

    @if_helethy
    async def get_position(self):
        self.__last_position = await self.parser.M114('R')
        if isinstance(self.__last_position, dict):
            self.__last_position.pop('F', None)
        return self.__last_position

    @if_helethy
    async def set_position(self, axis):
        if isinstance(axis, dict):
            await self.parser.G0(*axis.items())
            return axis
        elif isinstance(axis, (list, tuple)):
            await self.parser.G0(*axis)
            return GCODE.axis_tuple2dict(*axis)

    @if_helethy
    async def set_absolute(self, value=True):
        self.absolute = value
        await self.parser.G90() if value else await self.parser.G91()

    @if_helethy
    async def set_relative(self, value=True):
        await self.set_absolute(not value)

    @if_helethy
    async def set_position_and_wait(self, axis, interval=0.5, timeout=10):
        """
        Move to a specific position. And wait for current position to be reached.
        """

        future = await self.set_position(axis)
        future.pop('F', None)

        async def task():
            atual_position = await self.get_position()
            while not all([atual_position.get(key, None) == value for key, value in future.items()]):
                sas = await self.get_position()
                if isinstance(sas, dict):
                    atual_position = sas
                await self.webscoket_route.broadcast(self.update_status())
                await sleep(interval)
        await wait_for(task(), timeout=timeout)

    @property
    def helthly(self):
        return self.connected  and self.whiout_error #? and ...
    
    @property
    def connected(self):
        return getattr(self.parser, 'websocket', False) and self.parser.websocket.open
        
    def update_status(self):
        return {
            'type': 'machine',
            'id': self._id,
            'position': self.__last_position,
            'absolute': self.absolute,
            'helthly': self.helthly
        }
