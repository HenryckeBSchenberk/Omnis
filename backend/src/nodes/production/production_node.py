from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from .production_obj import ProductionOBJ
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "PRODUCTION"


@for_all_methods(exception(logger))
class ProductionNode(BaseNode):
    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.model = options["model"]["value"]
        self.status = None
        self.production_obj = ProductionOBJ(**options)
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        target = message.targetName.lower()
        if target == "start":
            self.production_obj.start()
        elif target == "finish":
            _ = self.production_obj.finish(model=self.model, status=self.status)
            self.onSuccess(_)
        elif target == "status":
            self.status = message.payload
