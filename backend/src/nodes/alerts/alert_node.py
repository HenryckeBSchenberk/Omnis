from src.nodes.alerts.alert_obj import Alert
from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer

NODE_TYPE = "AlertNode"

class AlertNode(BaseNode):
    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.input_connections = input_connections
        self.title = options["title"]
        self.level = options["level"]    
        self.title = options["title"]    
        self.description = options["description"]    
        self.how_to_solve = options["how_to_solve"]        
        self.button_text = options["button_text"]        
        self.button_action = options["button_action"]        
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message=""):
        Alert(self.title, self.level, self.title, self.description, self.how_to_solve, self.button_text, self.button_action)
