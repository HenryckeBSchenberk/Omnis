import asyncio
from src.nodes.process.process_node import ProcessNode
from api import logger
NODE_TYPE = "PauseNode"

class PauseNode(ProcessNode):
    def __init__(self, name, id, options, output_connections, input_connections):
        self.options = options
        self.options["action"] = "pause"
        self.options["auto_run"] = False
        super().__init__(name, id, options, output_connections, input_connections)

    async def execute(self, message):
        await super().execute(message)
        await self.__resume(message)

    async def __resume(self, message):
        while self.manager.process.is_paused():
            await asyncio.sleep(0.1)
            if self.manager.process.is_stopped():
                return
        else:
            self.on("Saida", message.payload)