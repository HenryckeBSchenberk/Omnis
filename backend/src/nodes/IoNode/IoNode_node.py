from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods
from api import dbo
from src.nodes.serial.manager import Manager as SerialManager
from src.utility.system.sleep_alternative import sleep
from bson import ObjectId
NODE_TYPE = "IoNode"


@for_all_methods(exception(logger))
class IoNodeNode(BaseNode):
    """
    insert_node_description_here
    """

    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections
        self.config = options["port"]
        self.board = SerialManager.get_by_id(ObjectId(self.config["board"]))
        self.command = self.config["command"].replace("<pin>", str(self.config["port"])).replace("<pwm>", str(255 if self.config["pwm"] else 0))
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)


    #@Observer.fail
    def execute(self, message=""):
        target = message.targetName.lower()
        if target == "gatilho":
            self.board.send(self.command)
            # sleep(0.3)
            self.on("Saida", message.payload)


    @staticmethod
    def get_info(**kwargs):
        return {
            "options": list(dbo.find_many("pins", {"board": kwargs.get("board")}, {"_id": 0}))
        }


# LC - Quad, SU, SIM. Mantem.
# Melhoraram os cortes e pinturas.

# SC
# LC - Quad, DU, SIM.
