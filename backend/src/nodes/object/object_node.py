from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode
from api import logger, exception
from api.decorators import for_all_methods
from src.nodes.object.object import Object, Manager as ObjectManager

NODE_TYPE = "ObjectNode"


@for_all_methods(exception(logger))
class ObjectNode(BaseNode):
    """
        Esse nó possui duas interfaces, uma de entrada e outra de saida.
        A interface de entrada é responsável por receber a alteração deseja ao objeto.
        A interface de saida é responsável por enviar a alteração realizada no objeto.

        O realiza as seguintes operações:
         - Recebe e processa a alteração a ser feita.
         - Atualiza os valores com base contexto do ObjectManager.
         - Exporta as atualizações para o banco de dados (sync: True).
         - Envia a alteração realizada para a interface de saída.

        - Options:
            - _id: Identificador do objeto a ser alterado.
            - content: Conteúdo a ser alterado.

    """

    def __init__(self, name, id, options, output_connections, input_connections):
        super().__init__(name, NODE_TYPE, id, options, output_connections)
        self.target_id = options.get("_id", None)
        # assert (self.target_id, "ObjectNode: Target id not defined.")

        self.input_connections = input_connections
        self.content = options.get("content", {})
        self.sync = options.get("sync", False)

        self.object = Object(self.target_id, **self.content)
        NodeManager.addNode(self)

    @BaseNode.Notify_Execution()
    async def execute(self, message=""):
        # assert(isinstance(message, dict), "ObjectNode: Message must be a dict.")

        self.object.load(**message)
        self.content = self.object.export()['content']
        self.on("Gatilho", self.content)
        if self.sync:
            self.sync_content()

    def sync_content(self):
        ObjectManager.update(
            _id=self.target_id,
            input={
                "content": self.content,
            },
            user=self.user
        )

    @staticmethod
    def get_info(**kwargs):
        return {
            "options": {
                "objects": list(ObjectManager.get_list(filter={"content": 1})),
            }
        }
