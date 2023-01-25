from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer

from api import logger, exception
from api.decorators import for_all_methods

from cv2 import (
    cvtColor,
    COLOR_BGR2HSV,
    COLOR_HSV2BGR,
    COLOR_BGR2RGB,
    COLOR_RGB2BGR,
    COLOR_BGR2GRAY,
    COLOR_GRAY2BGR,
)

NODE_TYPE = "COLORSPACE"

color_operations = {
    "BGR2HSV": COLOR_BGR2HSV,
    "HSV2BGR": COLOR_HSV2BGR,
    "BGR2RGB": COLOR_BGR2RGB,
    "RGB2BGR": COLOR_RGB2BGR,
    "BGR2GRAY": COLOR_BGR2GRAY,
    "GRAY2BGR": COLOR_GRAY2BGR,
}


@for_all_methods(exception(logger))
class ColorspaceNode(BaseNode):
    """
    insert_node_description_here
    """

    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections
        self.operation = options.color_space["value"]
        self.image = None
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        self.image = message.payload
        try:
            self.image = cvtColor(self.image, color_operations[self.operation])
            self.onSuccess(self.image)
        except Exception as e:
            self.onFailure(f"{self._id} cant execute.", pulse=True, errorMessage=str(e))

    def get_frame(self):
        return self.image

    @staticmethod
    def get_info(**kwargs):
        return {"options": {"color_space": list(color_operations.keys())}}
