import cv2
from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "COLORSPACE"


@for_all_methods(exception(logger))
class ColorSpaceNode(BaseNode):
    """
    Convert an image color format to another.
    More info about color conversion methods can be found here: https://docs.opencv.org/4.5.5/de/d25/imgproc_color_conversions.html
    More info about color conversion codes can be found here:    https://docs.opencv.org/4.5.5/d8/d01/group__imgproc__color__conversions.html
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections
        self.CSO = options["colorSpaceOrigin"]
        self.CSC = options["colorSpaceConvert"]
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        try:
            _ = cv2.cvtColor(
                message.payload, getattr(cv2, f"COLOR_{self.CSC}2{self.CSO}")
            )
            self.onSuccess(_)
        except Exception as e:
            self.onFailure("Cant execute action", pulse=True, errorMessage=str(e))
