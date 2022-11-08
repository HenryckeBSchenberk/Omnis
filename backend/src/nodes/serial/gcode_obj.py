from time import sleep
from timeit import default_timer as timer

from .custom_serial import Serial
from api import logger, exception
from api.decorators import for_all_methods
from api import logger
from threading import Event, Thread
from json import loads
from re import split
from src.end_points import Controls
import asyncio


@for_all_methods(exception(logger))
class SerialGcodeOBJ(Serial):
    def __init__(
        self,
        _id=None,
        port=None,
        name=None,
        baudrate=9600,
        filters={},
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=0.01,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
        is_gcode=True,
        disabled=False,
        startup_commands = [
            # "G28",           #! Not every board should start homming
        ],
        pins={},
        axes={}
    ):
        super().__init__(
            port,
            name,
            baudrate,
            filters,
            bytesize,
            parity,
            stopbits,
            timeout,
            xonxoff,
            rtscts,
            dsrdtr,
            is_gcode=True,
            _id=_id,
        )
        self.is_open = True
        self.resumed = Event()
        self.was_stopped = Event()
        self.timeout = 50 # Max time to wait for a response from the machine (G28 will take a while)
        self.resumed_permission = ["stop", "kill", "quick_stop", "resume"]
        self.__status = {"jog_position":{'X':0, 'Y':0, 'Z':0, 'A':0, 'B':0, 'C':0}}
        self.resume()
        for msg in startup_commands:
            self.super_send(msg)
        self.pins = pins
        self.axes = axes
        self.websocket = Controls(self._id, self)
        Thread(target=self.auto_update, name=f"{_id}_auto_update", daemon=True).start()

    def auto_update(self):
        asyncio.run(self.websocket.broadcast_on_change(self.status, self.status))


    
    def status(self):
        return self.__status


    def verify(function):
        def wrapper(self, *args, **kwargs):
            if not self.is_open or not self.resumed.is_set(): return
            return function(self, *args, **kwargs)
        return wrapper

    @verify
    def G28(self, axis=[]):
        self.super_send("G28" +' '.join(axis), echo=True)
        t0 = timer()
        while self.resumed.is_set() and ((timer()-t0) < self.timeout) and not self.M119({name.upper():'TRIGGERED' for name in axis}):
            sleep(0.3)
        self.M114('R')
        return True

    def M119(self, axis={}):
        if axis is not None:
            compare = []
            echo = self.super_send("M119", echo=True)
            if echo and not isinstance(echo, str) and echo.pop(0) == "Reporting endstop status" and echo.pop() == 'ok':
                for status in echo:
                    name, value = status.split(":")
                    if name in axis.keys():
                        compare.append(axis.get(name[0].upper(), value.replace(" ", "")) == value.replace(" ", ""))
                if all(compare): return True
                return False

    @verify
    def G0(self, *args, **kwargs):
        """
        Send a GCODE movement command (G0) and wait for current position to be reached.
        """
        # Create a coordinate string based in args.
        cords = ""
        for pos in args:
            cords += f"{pos[0].upper()}{round(float(pos[1]), 1)} "

        # Send machine to the coordinate string
        self.super_send(f"G1 {cords}")
        t0 = timer()
        while self.resumed.is_set() and ((timer()-t0) < self.timeout):
                try:
                    future = self.M114().items()
                    if future != 'FAIL': break
                except AttributeError as e:
                    logger.info(f"Can't get M114: {str(e)}")
                    sleep(0.3)
        else:
            raise AttributeError("SERIAL DEAD")
        while (
            any((self.resumed.is_set() and (round(v,1) != round(self.M114("R")[i],1))) for i, v in future) #! Round is mandatory
            

        ):
            # print(self.__status)
            continue
        else:
            if not self.resumed.is_set(): return
        last_pos = self.M114("R")
        for axis in self.axes.values():
            axis.position = last_pos[axis.name]
        return last_pos
    @verify
    def M114(self, _type="", sequence=["X", "Y", "Z", "E", ":"], *args, **kwargs):
        """
        Get current position of machine.
        _type:
            R - Return the current position of the machine, in real time.
            ''- Return the future postion of the machine.

        """
        for echo in self.super_send(f"M114 {_type}", echo=True, log=False):
            txt = echo
            for n in sequence:
                txt = txt.replace(n, "")
            try:
                _echo = dict(
                    zip(
                        sequence[:-1],
                        list(map(float, txt.split(" ")[: len(sequence) - 1])),
                    )
                )
                if _type == "R":
                    self.__status["jog_position"] = _echo
                    for axis in self.axes.values():
                        axis.position = _echo[axis.name]
                return _echo
            except ValueError as e:
                print('ValueError on M114:', e)
                return self.__status['jog_position']
                # if kwargs.get('counter', 0) < kwargs.get('max_tries', 3):
                #    return self.M114(_type, counter=kwargs.get('counter', -1)+1, max_tries=kwargs.get('max_tries', 3))
                # raise ValueError(f"Custom M114 can't decode {echo}")

    def M42(self, _id, _value):
        return super().send(self.pins[_id].set_value(_value)) if self.pins.get(_id) else False

    def send(self, msg, echo=False, log=True, *args, **kwargs):
        parms = list(
            filter(
                lambda x: x is not None and x != " " and x != "",
                split(
                    "(\(.*\))|(\{.*)| ",
                    msg,
                ),
            )
        )
        command_splited = list(map(SerialGcodeOBJ.parser, parms))
        if command_splited[0].startswith(">"):
            command_splited[0] = command_splited[0][1:]
        if all(isinstance(n, str) for n in command_splited):
            return super().send(msg, echo, log, *args, **kwargs)

        sender = getattr(self, command_splited[0].upper(), False)
        if sender:
            args = command_splited[1] if len(command_splited) > 1 else []
            kwargs = command_splited[-1] if isinstance(command_splited[-1], dict) else {}
            logger.debug(f"Serial: [Custom GCODE] {command_splited[0].upper()}: {sender(*args, **kwargs)}")
        else:
            logger.warning(f"Serial: [Custom GCODE] {command_splited[0].upper()} can't be found.")
            self.last_value_received=['Invalid: {}'.format(command_splited[0].upper())]
        return self

    def super_send(self, *args, **kwargs):
        return super().send(*args, **kwargs)

    def parser(string):
        if string.startswith("("):
            return eval(string)
        elif string.startswith("{"):
            return loads(string)
        return string

    # @verify
    def pause(self):
        """
        The M0 command pause after the last movement and wait for the user to continue.
        """
        self.send("G90")
        self.resumed.clear()
        
        # self.send("M0")

    @verify
    def kill(self):
        """
        Used for emergency stopping,
        M112 shuts down the machine, turns off all the steppers and heaters
        and if possible, turns off the power supply.
        A reset is required to return to operational mode.
        """
        # self.send("M112")                 #! Assert this config is enabled

    # @verify
    def stop(self):
        """
        Stop all steppers instantly.
        Since there will be no deceleration,
        steppers are expected to be out of position after this command.
        """
        self.pause()
        # self.send("P000")                #! Assert this config is enabled
        # self.resumed.clear()
        if not self.was_stopped.is_set():
            self.was_stopped.set()
        #     self.send("M410")
        #     self.send("M0")
        self.resume()

    def resume(self):
        """
        Resume machine from pause (M0) using M108 command.
        """
            # self.send("M108")
        # self.send("R000")                 #! Assert this config is enabled
        if self.was_stopped.is_set():
            # self.super_send("G28")        #! Assert this config is enabled
            self.was_stopped.clear()
        self.resumed.set()

    def __str__(self) -> str:
        return f"[[SerialGcodeOBJ] {self.name}, {self.port}, {self.baudrate}]"
