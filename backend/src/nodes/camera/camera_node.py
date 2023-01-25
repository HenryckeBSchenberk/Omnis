from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods
from .manager import Manager as CameraManager

NODE_TYPE = "CameraNode"

@for_all_methods(exception(logger))
class CameraNode(BaseNode):
    """
    Trigger it self every 'n' seconds.\n
    \n
    Signals -> \n
    \t:onSuccess: - Send last frame read.\n
    """

    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections
        self.camera_id = options["camera"]["_id"]
        self.camera = CameraManager.get_by_id(self.camera_id)
        self.auto_run = options.get("auto_run", {"value":False})["value"]
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message=""):
        self.on("Imagem", self.read())

    def read(self):
        return self.camera.read()

    @staticmethod
    def get_info(**kwargs):
        return {"options": "cameras"}
