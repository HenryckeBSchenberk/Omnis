from time import sleep
import timeit
from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode
from src.manager.serial_manager import SerialManager
from api import logger, exception
from os import popen
NODE_TYPE = "MOVEMENT"


class MovementNode(BaseNode):
    """
    A class to send movement commands GCODES trough an serial instace.

    """

    @exception(logger)
    def __init__(self, name, id, options, outputConnections, inputConnections) -> None:
        super().__init__(name, NODE_TYPE, id, options, outputConnections)
        self.inputConnections = inputConnections
        self.serial_id = options["hardware"]["serial_id"]
        self.serial = SerialManager.get_by_id(self.serial_id)
        self.axis = list(map(lambda x: x.lower(), options["axis"]["list_of_axis"]))
        self.trigger_delay = 10
        self.coordinates = {
            k.lower(): v
            for k, v in options["axis"]["values"].items()
            if k.lower() in self.axis
        }
        self.auto_run = options["auto_run"]["value"]
        print(name, self.auto_run)
        NodeManager.addNode(self)

    @exception(logger)
    def execute(self, message):
        #print(f"{self.name} recived: {message}, {type(message)}")
        action = message.targetName.lower()
        if action in self.axis:
            self.coordinates[action] = message.payload
        else:
            return getattr(self, action + "_f")(message.payload)


    @exception(logger)
    def coordinates_f(self, payload):
        for k, v in payload.items():
            self.coordinates[k] = v

    @exception(logger)
    def trigger_f(self, payload=None):
        if True or self.serial is not None and self.serial.is_open:
            movement = [
                (k, v)
                for k, v in self.coordinates.items()
               if (k in self.axis and v is not None)
            ]
            #print(f"{movement}")
            #self.serial.M_G0(*movement, sync=True)
            sleep(5)
            self.onSuccess(self.serial_id)

        else:
            if not self.serial.is_open:
                self.onFailure("Serial not running", pulse=True)

            if self.serial is None:
                self.onFailure("Serial not connected", pulse=True)

    @exception(logger)
    def stop(self):
        try:
            self.serial.stop()
        except AttributeError:
            pass

    @exception(logger)
    def resume(self):
        super().resume()

    @exception(logger)
    def pause(self):
        super().pause()
