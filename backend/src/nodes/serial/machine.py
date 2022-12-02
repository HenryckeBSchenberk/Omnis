from asyncio import sleep, wait_for
from api.websocket import ConnectionManager
from uuid import uuid4
from .gcode import GCODE
from datetime import datetime, timedelta


class Machine_Websocket_API(ConnectionManager):
    def __init__(self, _id, machine):
        super().__init__(_id, machine)
        self.machine = self.interface
        self.valid_context = [
            'position',
            'homing',
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
    
    def parser_finder(self, data):
        function = getattr(self, f"{data.get('method','').lower()}_{data.get('context','').lower()}", False)
        return function or self.get_help

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

    async def help_position(self, websocket, data=None):
        return await self.send_to(websocket, {
                'axis': "{Axis_Name:Desired_Position} | {X:100, Y:150, Z:..., ...}",
                'relative': '(True/Flase) -> G91 | G90',
                'wait': '(True/Flase) -> Will block until the machine has reached the desired position',
                'broadcast': '(True/Flase) -> Will broadcast the new position to all connected clients',
            })

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

    async def help_homing(self, websocket, data=None):
        return await self.send_to(websocket, {
                'axis': "(*Axis_Name) | (X, Y, Z, ...)",
                'mehtod_get': f'Will return if the machine has been homing in the last {self.machine.homing_trusted_time} minutes',
                'method_help': 'Will show this message',
            })

    async def set_homing(self, websocket, data):
        if data.get('axis'):
            await self.machine.homing(data.get('axis'))
        await self.get_homing(websocket, data)

    async def get_homing(self, websocket, data=None):
        await self.send_to(websocket, {'status':self.machine.homed, 'time_out':self.machine.homing_trusted_time})
    


class Machine:
    def __init__(self, parser, axis=None, pins=None, _id=None) -> None:
        self._id = _id or uuid4().hex
        self.__homed = [False, datetime.utcnow()]
        self.__last_position = {}
        self.whiout_error = True
        self.absolute = True
        self.homing_trusted_time = 10
        self.axis = axis
        self.pins = pins
        self.parser = parser
        self.webscoket_route = Machine_Websocket_API(self._id, self)
        self.parser._manager.add_device(self)

    async def __aenter__(self):
        await self.parser.connect()
        return self

    async def __aexit__(self, *args):
        await self.parser.websocket.close() #! Update wspyserial to provide .disconnect() insted

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

    async def homing(self, axis):
        if isinstance(axis, dict):
            axis = tuple(axis.keys())
        if await self.parser.G28(*axis):
            self.__homed = [True, datetime.utcnow()+timedelta(minutes=self.homing_trusted_time)]
        return

    @property
    def homed(self):
        if self.__homed[0]:
            if self.__homed[1] >= datetime.utcnow():
                return True
            self.__homed[0] = False
        return False

    @if_helethy
    async def set_homing(self, axis):
        await self.homing(axis)
        return self.homed

    async def get_homing(self):
        return self.homed

    @if_helethy
    async def get_position(self):
        new_pos= await self.parser.M114('R')
        if isinstance(new_pos, dict):
            new_pos.pop('F', None)
            self.__last_position = new_pos
            self.__update_axis_position(**new_pos)
        return self.__last_position

    def __update_axis_position(self, **axis):
        for name, value in axis.items():
            ax = self.axis.get(name, False)
            if ax: ax.set_position(value)

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
    async def set_position_and_wait(self, axis, interval=0.2, timeout=10):
        """
        Move to a specific position. And wait for current position to be reached.
        """
        #! intervall affect responsivity of the machine
        future = await self.set_position(axis)
        future.pop('F', None)

        async def task():
            atual_position = await self.get_position()
            while not all([atual_position.get(key, None) == value for key, value in future.items()]):
                await sleep(interval)
                sas = await self.get_position()
                if isinstance(sas, dict):
                    atual_position = sas
                await self.webscoket_route.broadcast(self.update_status())
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
            'helthly': self.helthly,
            'homed': self.homed,
            'axis': [axis.status for axis in self.axis.values()],
        }
