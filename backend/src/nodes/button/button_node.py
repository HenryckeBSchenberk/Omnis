from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from datetime import datetime
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "BUTTON"


@for_all_methods(exception(logger))
class ButtonNode(BaseNode):
    """
    Signals ->
    \t:onClick: - Envia um sinal de click. \n
    """

    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        """
        Executes the node.
        """

        self.on("onClick", datetime.now())

    def reset(self):
        """
        Resets the node.
        """
        return True
