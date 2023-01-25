from src.nodes.process.process_node import ProcessNode

NODE_TYPE = "StopNode"

class StopNode(ProcessNode):
    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        self.options = options
        self.options["action"] = "stop"
        self.options["auto_run"] = False
        super().__init__(name, id, options, output_connections, input_connections, default_object)