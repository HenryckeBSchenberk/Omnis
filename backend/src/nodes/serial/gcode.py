import asyncio
from wspyserial.protocol import package
from .client import CustomSerial as Serial
class PARSER:
    def readeable(func):
        def wrapper(pkg, *args, **kwargs):
            if pkg is not None: #! if user choose not read the package, it will be None
                assert isinstance(pkg, package), "readeable: pkg must be a package"
                if pkg.read:
                    return func(pkg.data, *args, **kwargs)
            return True #! If user choose not read the package, always return True
        return wrapper
        
    @readeable
    def G0(data):
        """
        Send a GCODE movement command (G0) and wait for current position to be reached.
        """
        return data[0] == 'ok'
    
    @readeable
    def G1(data):
        return data[0] == 'ok'
    
    @readeable
    def M42(data):
        return data[0] == 'ok'
    
    @readeable
    def M114(data, sequence=["X", "Y", "Z", "E", ":"]):
        """
        Get current position of machine.
        _type:
            R - Return the current position of the machine, in real time.
            ''- Return the future postion of the machine.

        """
        for echo in data:
            if echo == "ok": continue
            txt = echo
            for n in sequence: txt = txt.replace(n, "")
            if txt is None: return False
            try:
                return dict(
                    zip(
                        sequence[:-1],
                        list(map(float, txt.split(" ")[: len(sequence) - 1])),
                    )
                )
            except ValueError:
                print("M114: ValueError, txt:", txt)
                return False
    
    @readeable
    def M119(data, axis={}):
        if axis is not None:
            compare = []
            if data and not isinstance(data, str) and data.pop(0) == "Reporting endstop status" and data.pop() == 'ok':
                for status in data:
                    name, value = status.split(":")
                    if name in axis.keys():
                        compare.append(axis.get(name[0].upper(), value.replace(" ", "")) == value.replace(" ", ""))
                if all(compare): return True
                return False


class GCODE:
    def axis_tuple2string(*axis):
        command = ""
        for axi in axis:
            if axi is not None:
                command += f"{axi[0].upper()}{round(float(axi[1]), 2)} "
        return command

    def axis_tuple2dict(*axis):
        return dict(zip([axi[0].upper() for axi in axis], [round(float(axi[1]),2) for axi in axis]))

    def G0(*axis):
        """
        Move to a specific position.
        """
        command = GCODE.axis_tuple2string(*axis)
        return package(F"G0 {command}", 1, read=False)

    def G1(*axis):
        """
        Move to a specific position.
        """
        command = GCODE.axis_tuple2string(*axis)
        return package(f"G1 {command}", 1, read=False)

    def M42(pin, value):
        """
        Set pin value.
        """
        return package("M42 P{} S{}".format(pin, value), 1, read=False)

    def M114(_type=""):
        """
        Get current position of machine.
        _type:
            R - Return the current position of the machine, in real time.
            ''- Return the future postion of the machine.
        """
        return package(f"M114 {_type}", 2)

    def M119(sensors_qtd=6):
        """
        Get endstop status.
        """
        return package("M119", sensors_qtd)
    
    def G28():
        """
        Home all axis.
        """
        raise NotImplementedError('G28 is not implemented yet')

class Client(Serial):
    def __init__(self, host, port) -> None:
        super().__init__(host, port)
        self.__position = {'X': 0, 'Y': 0, 'Z': 0, 'E': 0}

    def parser(func):
        """
        Decorator to parse the package.
        """
        async def wrapper(*args, **kwargs):
            data = await func(*args, **kwargs)
            function_name = func.__name__
            function_parser = getattr(PARSER, function_name, False)
            if not function_parser:
                #! Should warn user that there is no parser for this function.
                return data
            return function_parser(data)
        return wrapper

    @parser
    async def G0(self, *axis):
        return await self.send(GCODE.G0(*axis))
    
    @parser
    async def G1(self, *axis):
        return await self.send(GCODE.G1(*axis))
    
    @parser
    async def M42(self, pin, value):
        return await self.send(GCODE.M42(pin, value))
    
    @parser
    async def M114(self, _type=""):
        return await self.send(GCODE.M114(_type))
    
    @parser
    async def M119(self, sensors_qtd=6):
        return await self.send(GCODE.M119(sensors_qtd))

    @parser
    async def G28(self):
        raise NotImplementedError("G28 is not implemented yet")

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        if isinstance(value, dict):
            self.__position = value

    async def GOTO(self, *axis, interval=0.1, timeout=10):
        """
        Move to a specific position. And wait for current position to be reached.
        """

        future = GCODE.axis_tuple2dict(*axis)
        future.pop('F', None)

        async def task():
            await self.G0(*axis)
            self.position = await self.M114('R')
            while not all([self.position.get(key, None) == value for key, value in future.items()]):
                self.position = await self.M114('R')
                await asyncio.sleep(interval) #! Avoid buffer overflow
        await asyncio.wait_for(task(), timeout=timeout)
