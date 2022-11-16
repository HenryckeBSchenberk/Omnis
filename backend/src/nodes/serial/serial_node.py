from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Wizard
from src.nodes.timer.task_time import setInterval
from src.nodes.serial.manager import Manager as SerialManager
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "SERIAL"


@for_all_methods(exception(logger))
class SerialNode(BaseNode):
    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections
        self.serial_id = options["hardware"]["serial_id"]
        self.serial = SerialManager.get_by_id(self.serial_id)
        self.stop_event = self.execute()
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    @setInterval(1)
    @Wizard._decorator
    def execute(self, message=""):
        if not self.serial.is_open:
            self.serial.start()
            self.onSuccess(self.serial)
            self.on("serial", self.serial)
            return True
        else:
            self.onSuccess(self.serial)
            return True

    def stop(self):
        self.stop_event.set()

    def reset(self):
        self.stop_event = self.execute()
