from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer

from api import logger, exception
from api.decorators import for_all_methods
from src.manager.camera_manager import CameraManager
from src.nodes.color.color_obj import ColorOBJ
from cv2 import (
    COLOR_BGR2HSV_FULL,
    inRange,
    cvtColor,
    COLOR_BGR2HSV,
    bitwise_and,
    FONT_HERSHEY_SIMPLEX,
    putText,
    imread,
    resize,
    imwrite
)

from numpy import array

NODE_TYPE = "HsvFilterNode"


@for_all_methods(exception(logger))
class HsvNode(BaseNode):
    """
    HsvNode is a class to convert an image to HSV color space and filter it by a color range.

    Signals ->
        "HSV Mask" -> returns the filtered color range in HSV color space.
        "Better HSV" -> returns the same at above but with an MorphologyEx applied to remove noise pixels.
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.update_options(options)
        self.auto_run = options.get("auto_run", False)
        self.image = CameraManager.read()
        NodeManager.addNode(self)
        CameraManager.add(self)

    #@Observer.fail
    def execute(self, message):
        target = message.targetName.lower()
        if target == "color_range":
            self.color_range = message.payload
        elif target == "imagem":
            self.image = message.payload
            self.on("Saida", self.convert_frame(
                    self.image,
                    self.color_range["lower"],
                    self.color_range["upper"],
                ))

    @staticmethod
    def convert_frame(image, lower, upper):
        return inRange(
            cvtColor(image, COLOR_BGR2HSV_FULL),
            array(lower),
            array(upper)
        )

    def read(self):
        return bitwise_and(self.image, self.image, mask=self.convert_frame(
                    self.image,
                    self.color_range["lower"],
                    self.color_range["upper"],
                ))

    def update_options(self, options):
        self.color_range = {
            "lower": ColorOBJ(options["lower"]["rgb"], "RGB").get("CV2_HSV"),
            "upper": ColorOBJ(options["upper"]["rgb"], "RGB").get("CV2_HSV"),
        }
    def stop(self):
        super().stop()
        CameraManager.remove(self)

    @staticmethod 
    def stream_frame(frame, lower, upper):
        return HsvNode.convert_frame(frame, lower, upper)