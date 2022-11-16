from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Wizard
from src.nodes.serial.manager import Manager as SerialManager
from api import logger, exception
from api.decorators import for_all_methods
from bson import ObjectId
from collections import Counter
from threading import Event
NODE_TYPE = "MoveAxisNode"


@for_all_methods(exception(logger))
class MovementNode(BaseNode):
    """
    A class to send movement commands GCODES trough an serial instace.

    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections
        self.serial_id = ObjectId(options["board"]["id"])
        self.serial = SerialManager.get_by_id(self.serial_id)
        if not self.serial: raise TypeError("SERIAL DEAD")
        self.serial.resume()
        self.axis = []
        self.coordinates = {}
        self.special_coordinates = {}
        self.wait_for_this = [{k.lower():v for k,v in x['to'].items() if k == "name"} for x in self.input_connections]
        self.trigger = Event()
        self.has_trigger = {"name":"Gatilho"} in self.wait_for_this
        if self.has_trigger:
            self.wait_for_this.remove({"name":"Gatilho"})
            if len(self.wait_for_this) == 0:
                self.trigger.set()
        else:
            self.trigger.set()
            
        self.wait_checks = 0
        self.homing_axis =[]
        for axis in options["axislist"]:
            if axis.get('homing'): self.homing_axis.append(axis['name'].upper())
            if axis["isActive"]:
                self.axis.append(axis["name"].lower())
                if (str(axis['value']).startswith('!')):
                    self.special_coordinates[axis["name"].lower()] = float(axis['value'][1:])
                else:
                    self.coordinates[axis["name"].lower()] = float(axis['value'])

        self.relative = options.get("relative", False)
        self.trigger_delay = 2
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    @Wizard._decorator
    def execute(self, message):
        action = message.targetName.lower()
        if action in self.axis:
            self.coordinates[action] = message.payload
        elif action == "xy":
            self.coordinates_f(message.payload)
        if (self.wait_checks >= len(self.wait_for_this)) and self.has_trigger: self.trigger.set()
        if (action == "gatilho" and  self.trigger.wait(120)) or ((self.wait_checks >= len(self.wait_for_this)) and not self.has_trigger):
            if self.has_trigger: self.trigger.clear()
            if any(self.homing_axis):
                self.serial.G28(self.homing_axis)
            self.gatilho_f()
        # else:
        #     logger.info(f"{action}, {self.trigger.is_set()}")
        #     self.on("Falha", "Invalid action")
        #     raise TypeError("Invalid action")

    def coordinates_f(self, payload):
        try:
            for k, v in payload.items():
                self.coordinates[k.lower()] = v
            self.wait_checks+=1
        except AttributeError:
            self.on("Falha", "Invalid payload")

    # ToDo time for wait after movement needs to be set on options.
    def gatilho_f(self):
        self.wait_checks = 0
        # return
        if self.serial is not None and self.serial.is_open:
            pre_move = Counter(self.coordinates.copy())
            pre_move.update(Counter(self.special_coordinates.copy()))
            movement = [
                (k, v)
                for k, v in pre_move.items()
                if v is not None
            ]

            # if (pre_move.get('y',0) - self.coordinates.get('y',0)) > 2: logger.error(f"Valor de offset muito alto: {pre_move['y'] - self.coordinates['y']}")
            # t = 0.5  # ! Remove this line

            # if self.relative:
            #     self.serial.send("G91", log=False)
            #     # t = 1  # ! Remove this line
            # else:
            #     self.serial.send("G90", log=False)
            self.serial.G0(*movement)
            self.on("Sucesso", self.serial_id)


        else:
            if not self.serial.is_open:
                self.on("Falha","Serial not running", pulse=True)

            if self.serial is None:
                self.on("Falha","Serial not connected", pulse=True)

    #! Marlin sometimes doesn't Homming after stop commands.
    def stop(self):
        self.serial.stop()
        super().stop()
        # self.serial.resume()

    def resume(self):
        self.serial.resume()
        super().resume()

    def pause(self):
        self.serial.pause()
        super().pause()

    def get_info(**kwargs):
        return {"options": SerialManager.get_info()}
