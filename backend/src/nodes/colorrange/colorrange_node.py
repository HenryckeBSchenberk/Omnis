from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "COLORRANGE"


@for_all_methods(exception(logger))
class ColorrangeNode(BaseNode):
    """
    Group two colors in a dictionary
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections
        self.lower = None
        self.upper = None
        # self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message=None):
        if message.targetName in ["lower", "upper"]:
            setattr(self, message.targetName, message.payload["lower"])

        if self.lower and self.upper:
            self.onSuccess({"lower": self.lower, "upper": self.upper})
            self.lower, self.upper = None, None

    @staticmethod
    def get_info(**kwargs):
        return {
            "options": {
                "option_name": "option_accepted_values",
            }
        }
