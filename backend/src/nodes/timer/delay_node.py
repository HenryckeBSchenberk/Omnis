from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods
# from src.utility.system.sleep_alternative import sleep
import asyncio
NODE_TYPE = "DelayNode"


@for_all_methods(exception(logger))
class DelayNode(BaseNode):
    """
    insert_node_description_here
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        NodeManager.addNode(self)

    #@Observer.fail
    async def execute(self, message=""):
        #sanity check
        if not str(self.options["delay"]).isnumeric():
            logger.warn(f'[{self.name}] || delay is not numeric "{self.options["delay"]}"')
            self.options["delay"] = "0.1"
        await asyncio.sleep(float(self.options["delay"]))
        self.on("Saida", message)