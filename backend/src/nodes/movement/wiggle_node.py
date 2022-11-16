from src.nodes.base_node import BaseNode, Wizard
from src.nodes.serial.manager import Manager as SerialManager
from src.nodes.node_manager import NodeManager
from api import logger
from bson import ObjectId
from threading import Event
NODE_TYPE = "PositionAdjustmentNode"


"""
options:
axisListDialog
mode
zStep
repetitions
invert
divider
velocity['value']
board
"""
class WiggleNode(BaseNode):
    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        # logger.info(options)
        self.axisList = options["axislist"]
        self.mode = options["mode"]
        self.zStep = options["zstep"]
        self.repetitions = options["repetitions"]
        self.invert = options["invert"]
        self.divider = options["divider"]
        self.velocity = options["velocity"]['value']
        self.board = options["board"]
        self.input_connections = input_connections
        self.coordinates = {}
        # logger.info(self.board)
        self.serial = SerialManager.get_by_id(ObjectId(self.board['id']))
        if not self.serial: raise TypeError("SERIAL DEAD")
        self.serial.resume()

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
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)
    @Wizard._decorator
    def execute(self, message):
        logger.info("EXECUTING")
        action = message.targetName.lower()
        if action == "xy":
            self.xy(message.payload)
        if (self.wait_checks >= len(self.wait_for_this)) and self.has_trigger: self.trigger.set()
        if (action == "gatilho" and  self.trigger.wait(120)) or ((self.wait_checks >= len(self.wait_for_this)) and not self.has_trigger):
            # logger.info("Wiggle")
            if self.has_trigger: self.trigger.clear()
            self.wiggle()
        # elif action == "x":
        #     self.x(message.payload)
        # elif action == "y":
        #     self.y(message.payload)
        # elif action == "z":
        #     self.z(message.payload)
        
        # else:
        #     logger.info("")
        #     self.on("Falha", "Invalid action")
        #     raise TypeError("Invalid action")

    def wiggle(self):
        for i in range(self.repetitions):
            coordinates = {}
            for axis in self.axisList:
                coordinates[axis['name'].lower()] = {'min':None, 'max':None}
                for signal in ['min', 'max']:
                    value = self.coordinates[axis['name'].lower()]+(float(axis[signal])/(float(self.divider*i) if i != 0 else 1))
                    # logger.info(value)
                    coordinates[axis['name'].lower()][signal] = value
                    # logger.info(f"{coordinates}, {self.coordinates}, {axis}")
            start_signal = ['min', 'max'] if self.invert['direction'] else ['max', 'min']
            start_axis =   ['Y', 'X'] if self.invert['axis'] else ['X', 'Y']
            self.serial.G0(*[
                (k, v)
                for k, v in self.coordinates.items()
                if v is not None
                ])
            for axis in start_axis:
                self.serial.G0(*[
                        (k, v)
                    for k, v in self.coordinates.items()
                    if v is not None
                    ])

                for signal in start_signal:
                    # logger.info(f"Moving {axis} to {coordinates[axis.lower()][signal]}")
                    pos = [(axis.lower(), coordinates[axis.lower()][signal]), ('F', self.velocity)]
                    self.serial.G0(*pos)
                                    # logger.info(self.coordinates)
            self.serial.G0(*[
                (k, v)
                for k, v in self.coordinates.items()
                if v is not None
                ])
            self.serial.send("G91")
            self.serial.G0(*[('Z', (self.zStep/(float(self.divider*i) if i != 0 else 1))), ('F', self.velocity)])
            self.serial.send("G90")
        self.serial.G0(*[
                (k, v)
                for k, v in self.coordinates.items()
                if v is not None
        ])
        self.on('Sucesso', 'Movimento realizado com sucesso')

    def xy(self, payload, axis=None):
        for k, v in payload.items():
            self.coordinates[k.lower()] = v
        self.wait_checks+=1
    
#Axis List = [{"name": "X", "min":-10, "max":10}]
# cord{x}{min}