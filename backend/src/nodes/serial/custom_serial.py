from datetime import datetime
from multiprocessing import Event
from telnetlib import ECHO
from serial.tools import list_ports
from serial import Serial as _Serial, serialutil
from bson import ObjectId
from src.manager.serial_manager import SerialManager
from api import logger, exception
from api.decorators import for_all_methods
from threading import Lock
import queue

send_lock = Lock()


@for_all_methods(exception(logger))
class Serial(_Serial):
    """
    Class to comunicate with serial port.

    Attributes:
        port (str): Port to comunicate.
        baudrate (int): Baudrate to comunicate.
        is_open (bool): True if port is open.
        is_gcode (bool): True if port is gcode.
        last_value_send (str): Last value send.
        last_value_received (str): Last value received.

    Methods:
        start: Open port.
        close: Close port.
        reset: Close and open port.
        send: Send message to port.
        echo: Read message from port.
        findMostCompatiblePort: Find most compatible port.
        to_dict: Return a dictionary representation of this class instance.

    Notes:
        when a serial port is opened, it is added to the SerialManager.
        when a serial port is closed, it is removed from the SerialManager.

        findMostCompatiblePort:

    """

    def __init__(
        self,
        port=None,
        name=None,
        baudrate=9600,
        filters={},
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
        is_gcode=False,
        _id=None,
    ) -> None:
        self._id = ObjectId(_id)
        try:
            super().__init__(
                port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, dsrdtr
            )
        except Exception:
            self.is_open = False
        else:
            self.is_open = True
        self.port = port
        self.baudrate = baudrate
        self.is_gcode = is_gcode
        
        self.last_value_send = None
        self.last_value_received = None

        if name is None:
            self.name = self.vid + self.pid + "_" + self.device
        else:
            self.name = name

        self.filters = filters
        self.__comands = queue.Queue()
        self.__echos = queue.Queue()
        self.answers = {}
        self.__signals = queue.Queue()
        SerialManager.add(self)

    def start(self):
        if not self.is_open:
            if self.port is None:
                compatible = self.findMostCompatiblePort()
                if compatible is not None:
                    for k, v in compatible.__dict__.items():
                        setattr(self, k, v)
                    self.port = self.device
            assert (
                self.port is not None
            ), "Port is not set and no compatible filter found!"
            self.open()
        return self

    def close(self):
        super().close()

    def stop(self):
        self.close()
        return self

    def remove(self):
        SerialManager.remove(self)

    def reset(self):
        self.close()
        self.start()
        return self

    def send(self, message, echo=False, log=True):

        # ID = ObjectId()
        # event = Event()
        # if echo:
        #     self.__signals.put((event,ID))
        # self.__comands.put((message, echo))
        # if echo:
        #     event.wait()
        #     return self.answers.pop(ID, None)
        # return self
        answer = self.write(message)
        if echo: return answer

    def __command_writer(self):
        while True:
            try:
                message, echo = self.__comands.get()
                # try:
                _echo = self.write(message)
                # except serialutil.PortNotOpenError:
                #     self.open()
                #     _echo = self.write(message)
                
                if echo:
                    event, ID = self.__signals.get()
                    self.__echos.put((_echo, ID, event))
            finally:
                self.__comands.task_done()

    
    
    def __command_reader(self):
        while True:
            try:
                _echo, ID, event = self.__echos.get()
                self.answers[ID] = _echo
                event.set()
            finally:
                self.__signals.task_done()
                self.__echos.task_done()


    def write(self, payload):
        echo = 'FAIL'
        try:
            send_lock.acquire()
            # if payload != self.last_value_send: logger.debug(f"Serial: {self.name} send: {payload}")
            super().write((f"{payload}\n").encode("ascii"))
            self.last_value_send = payload
            echo = self.echo()
        finally:
            send_lock.release()
            return echo

    def echo(self):
        lines = []
        _b = self.readline()
        while _b != b"":
            try:
                lines.append(_b.decode("ascii").rstrip())
            except UnicodeDecodeError:
                logger.warning(f'cant decode serial input: {_b}')
                pass
            if self.inWaiting() != 0: _b = self.readline()
            else: break
        self.last_value_received = lines
        return lines

    def findMostCompatiblePort(self):
        ports = {}
        port_list = {f"{p.vid}{p.serial_number}": p for p in list_ports.comports()}
        for port_id, port in port_list.items():
            match = 0
            for filter_key, filter_value in self.filters.items():
                if filter_value != -1 and getattr(port, filter_key) == filter_value:
                    match += 1
            if match > 0:
                ports[port_id] = match
        if ports:
            return port_list.get(max(ports, key=ports.get))

    def to_dict(self):
        return {
            "_id": self._id,
            "port": self.port,
            "name": self.name,
            "baudrate": self.baudrate,
            "is_open": self.is_open == True,
            "is_gcode": self.is_gcode == True,
            "last_value_send": self.last_value_send,
            "last_value_received": self.last_value_received,
            "date": datetime.timestamp(datetime.utcnow()),
        }