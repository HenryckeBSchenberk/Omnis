from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods

NODE_TYPE = "IfNode"


@for_all_methods(exception(logger))
class SwitchNode(BaseNode):
    """
    insert_node_description_here
    """

    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections
        self.variables = list(map(lambda x: x["name"], options["inputlist"]))#[chr(i) for i in range(ord("a"), ord("z") + 1)]
        self.inputs = {}
        self.expression = options["expression"]
        self.auto_run = options.get("auto_run", False)
        self.results = {True:options["onsuccess"], False: options["onfailure"]}
        self.translator ={"Verdadeiro":True, "Falso":False}
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message=""):
        target = message.targetName
        if target in self.variables:                                           #? Esperar todas as variaveis? similar ao de movimentação?
            self.inputs[str(target)] = message.payload
            result = eval(self.expression, self.inputs.copy())
            self.on("Sucesso" if result else "Falha", self.results[result])
        elif target in ["Verdadeiro", "Falso"]:
            self.results[self.translator[target]] = message.payload
        

    @staticmethod
    def get_info(**kwargs):
        return {
            "options": {
                "option_name": "option_accepted_values",
            }
        }