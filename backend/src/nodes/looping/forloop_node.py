from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from api import logger, exception
from api.decorators import for_all_methods
from src.manager.process_manager import ProcessManager as process

NODE_TYPE = "FORLOOP"


@for_all_methods(exception(logger))
class ForloopNode(BaseNode):
    """
    Interfaces ->
        :Lista: - Recebe uma lista como payload e salva no iterator. \n
        :Trigger: - Recebe um trigger como payload e executa o next(iterator). \n
    \n
    Signals ->
        :item: - Envia o item atual do iterator. \n
        :Fim: - Envia um sinal de fim de execução, reseta o iterator. \n
    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.iterator = enumerate(options["iterator"]["value"])
        self.backup = options["iterator"]["value"][:]
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        target = message.targetName

        if target == "next" or "auto_run":
            if target == "iterator":
                self.iterator = message.payload
            if not self.stop_event.is_set():
                try:
                    self.item_id, self.item = next(self.iterator)
                    self.on("item", self.item)
                except StopIteration:
                    process.stop(wait=False)
                    self.on("end", "")
        else:
            # ? This is necessary?
            raise "Target not found"

    def reset(self):
        super().reset()
        self.iterator = enumerate(self.backup[:])
