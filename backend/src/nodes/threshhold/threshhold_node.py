from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer

from cv2 import (
    threshold,
    THRESH_BINARY,
    THRESH_BINARY_INV,
    THRESH_TRUNC,
    THRESH_TOZERO,
    THRESH_TOZERO_INV,
    THRESH_OTSU,
    adaptiveThreshold,
    ADAPTIVE_THRESH_GAUSSIAN_C,
    ADAPTIVE_THRESH_MEAN_C,
)
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "THRESHHOLD"

thresh_types = {
    "BINARY": THRESH_BINARY,
    "BINARY_INV": THRESH_BINARY_INV,
    "TRUNC": THRESH_TRUNC,
    "TOZERO": THRESH_TOZERO,
    "TOZERO_INV": THRESH_TOZERO_INV,
    "OTSU": THRESH_OTSU,
}

thresh_means = {"GAUSSIAN": ADAPTIVE_THRESH_GAUSSIAN_C, "MEAN": ADAPTIVE_THRESH_MEAN_C}
thresh_functions = {
    "otsu": lambda GGBI, th_type: threshold(
        GGBI, 0, 255, thresh_types[th_type] | THRESH_OTSU
    )[1],
    "adaptative": lambda GGBI, th_type, th_mean, areas, C: adaptiveThreshold(
        GGBI, 255, thresh_means[th_mean], thresh_types[th_type], areas, C
    ),
}


@for_all_methods(exception(logger))
class ThreshholdNode(BaseNode):
    """
    insert_node_description_here
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections

        self.function = options.thresh_function.get("function").lower()
        if self.function == "adaptative":
            self.thresh_type = options.thresh_type.get("value").upper()
            self.thresh_mean = options.thresh_mean.get("value").upper()
            self.thresh_areas = options.thresh_areas.get("value")
            self.thresh_C = options.thresh_C.get("value")
            self.args = (self.thresh_mean, self.thresh_areas, self.thresh_C)

        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        self.image = message.payload
        try:
            self.thresh = thresh_functions[self.function](
                self.image, self.thresh_type, *self.args if self.args else None
            )
            self.onSuccess("thresh")
        except Exception as e:
            self.onFailure(f"{self._id} cant execute.", pulse=True, errorMessage=str(e))

    def get_frame(self):
        return self.image

    @staticmethod
    def get_info(**kwargs):
        return {
            "options": {
                "thresh_types": list(thresh_types.keys()),
                "thresh_means": list(thresh_means.keys()),
                "thresh_functions": list(thresh_functions.keys()),
            }
        }
