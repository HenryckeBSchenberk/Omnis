from wspyserial.protocol import package
from .client import CustomSerial as Serial

class PARSER:
    """
    Process data from serial port using specific GCODE parser for each GCODE command.

    An parser should alwayes be decorated with @readeable decorator.
    An parser function must receive only a data argument, from a package object.
    """
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
            ''- Return the future position of the machine.

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
    def M119(data, axis={}, boolean_return=False):
        individual = {}
        axis = {k.lower(): v for k, v in axis.items()}
        if data and not isinstance(data, str) and data.pop(0) == "Reporting endstop status" and data.pop() == 'ok':
            for status in data:
                name, value = status.split(":")
                
                value = value.strip().lower()
                name = name.lower()

                if name in axis:
                    individual[name] = (axis[name] == value)

            if boolean_return:
                return all(individual.values())
            return individual

    @readeable
    def G28(data):
        return set(['echo:busy: processing', 'ok']).issubset(set(data))

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
            ''- Return the future position of the machine.
        """
        return package(f"M114 {_type}", -1)

    def M119(sensors_qtd=-1):
        """
        Get endstop status.
        """
        return package("M119", sensors_qtd)
    
    def G28(*axis):
        """
        Home all axis.
        """
        return package("G28 "+" ".join(f'{a}' for a in axis), -1, 200)

class Client(Serial):
    def __init__(self, host, port, _id=None) -> None:
        super().__init__(host, port, _id=_id)

    def parser(func):
        """
        Decorator to parse the package.
        """
        async def wrapper(*args, **kwargs):
            data = await func(*args, **kwargs)
            function_name = func.__name__
            function_parser = getattr(PARSER, function_name, False)
            if not function_parser:
                return data
            if isinstance(args[0], Client):
                args = args[1:] # Parsers can't handle the client object as 'self'.
            x = function_parser(data, *args, **kwargs)
            return x
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
    async def M114(self, sequence=["X", "Y", "Z", "E", ":"]):
        return await self.send(GCODE.M114('R'))
    
    @parser
    async def M119(self, axis={}, boolean_return=False):
        return await self.send(GCODE.M119())

    @parser
    async def G28(self, *axis):
        return await self.send(GCODE.G28(*axis))
