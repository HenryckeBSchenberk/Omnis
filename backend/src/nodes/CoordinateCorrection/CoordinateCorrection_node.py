from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "COORDINATECORRECTION"


@for_all_methods(exception(logger))
class CoordinateCorrectionNode(BaseNode):
    """
    insert_node_description_here
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections

        self.cords = {}
        self.scale = options["scale"]
        self.offset = options["offset"]

        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message=""):
        self.output = {}

        if message.targetName == "coords":
            self.cords = message.payload

        # multiply by scale and sum offset in each dimension
        if self.cords is not None:
            for c, s, v in zip(
                self.cords.items(), self.scale.values(), self.offset.values()
            ):
                self.output[c[0]] = (c[1] * s) + v
        self.onSuccess(self.output)

    @staticmethod
    def get_info(**kwargs):
        return {"options": {}}
