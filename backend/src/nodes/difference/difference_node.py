from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "DIFFERENCE"


@for_all_methods(exception(logger))
class DifferenceNode(BaseNode):
    """
    insert_node_description_here
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections

        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message=""):
        try:
            self.onSuccess()
        except Exception as e:
            self.onFailure(f"{self._id} cant execute.", pulse=True, errorMessage=str(e))
