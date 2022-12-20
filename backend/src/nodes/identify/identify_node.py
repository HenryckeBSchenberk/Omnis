from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer

from .identify_functions import identifyObjects
from api import logger, exception
from api.decorators import for_all_methods
from api import dbo

NODE_TYPE = "IdentifyNode"


@for_all_methods(exception(logger))
class IdentifyNode(BaseNode):
    """
    Find a list of countours in an image that match a giver filters.

    Signals ->
        "onSuccess" -> returns a list of dimensional countour data.
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections
        self.filters = options["filters"]
        # self.propertie = options["propertie"]
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        object_data_list = identifyObjects(message.payload, **self.filters)
        self.on("MatrizOut", object_data_list)

    @staticmethod
    def get_info(**kwargs):
        return {"options": list(dbo.find_many("identify_node_info", {}, {"_id": 0}))}
