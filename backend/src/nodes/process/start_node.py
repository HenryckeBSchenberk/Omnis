from src.nodes.process.process_node import ProcessNode

NODE_TYPE = "StartNode"

class StartNode(ProcessNode):
    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        self.options = options
        self.options["action"] = "start"
        self.options["auto_run"] = True
        super().__init__(name, id, options, output_connections, input_connections, default_object)