from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from src.nodes.compare.compare_obj import data_comparatives
from api import exception, logger, for_all_methods

NODE_TYPE = "COMPARATIVE_DIMENSIONAL_DATA"


@for_all_methods(exception(logger))
class ComparedimensionaldataNode(BaseNode):
    """
    Node to execute logical operations between values.
    """

    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections
        self.operation = options["operation"]
        self.value2 = options["value2"]
        self.value3 = options["value3"]
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message=""):
        target = message.targetName.lower()
        getattr(self, target)(message)
        pass

    def dimensional_obj(self, message):
        self.dimensional_obj = message.payload

    def value2(self, message):
        self.value2 = message.payload

    def value3(self, message):
        self.value3 = message.payload

    def trigger(self, message):
        try:
            self.onSuccess(
                data_comparatives[self.operation](
                    self.dimensional_obj, self.value2, self.value3
                )
            )
        except Exception as e:
            self.onFailure(f"{self._id} cant execute.", pulse=True, errorMessage=str(e))
