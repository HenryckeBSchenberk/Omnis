from src.nodes.node_manager import NodeManager
from src.nodes.base_node import BaseNode, Observer
from src.nodes.serial.manager import Manager as SerialManager
from api import logger, exception
from api.decorators import for_all_methods
from bson import ObjectId
from collections import Counter
from threading import Event
NODE_TYPE = "MoveAxisNode"


@for_all_methods(exception(logger))
class MovementNode(BaseNode):
    """
    A class to send movement commands GCODES trough an serial instace.

    """
    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections
        self.serial_id = ObjectId(options["board"]["id"])

        # Pega a instancia da serial correspondente
        self.serial = SerialManager.get_by_id(self.serial_id)
        if not self.serial: raise TypeError("SERIAL DEAD")

        self.non_blocking = options.get("nonBlocking", False)

        self.trigger = Event()
        self.axis = []
        self.homing_axis = []
        self.coordinates = {}
        self.special_coordinates = {}
        self.activated_interfaces = 0

        # Separa as interfaces de entrada selecionadas em uma lista de 
        self.selected_interfaces = self.__selected_interfaces()

        self.has_trigger_interface = {"name":"Gatilho"} in self.selected_interfaces

        if self.has_trigger_interface:
            self.selected_interfaces.remove({"name":"Gatilho"})
            if len(self.selected_interfaces) == 0:
                self.trigger.set()
        else:
            self.trigger.set()
        
        for axis in options["axislist"]:
            # Adiciona como homing se estiver marcado
            if axis.get('homing'): self.homing_axis.append(axis['name'].upper())

            # Separa caso possua um valor inicial
            if axis["isActive"]:
                self.axis.append(axis["name"].lower())

                # Verifica se o valor inicial é um valor especial (RELATIVO)
                if (str(axis['value']).startswith('!')):
                    self.special_coordinates[axis["name"].lower()] = float(axis['value'][1:])
                else:
                    self.coordinates[axis["name"].lower()] = float(axis['value'])

        NodeManager.addNode(self)

    # #@Observer.fail
    async def execute(self, message):
        async with self.serial:
            # Recebe a interface de execução
            action = message.targetName.lower()

            # Verifica se a interface é um eixo unico, e atualiza o valor do eixo
            if action in self.axis:
                self.coordinates[action] = message.payload

            # Caso seja um conjunto de eixos, atualiza todos os eixos
            elif action == "xy":
                self.update_multiple_coordinates(message.payload)

            # Verifica se todas as interfaces dependentes foram atualizadas
            if (self.activated_interfaces >= len(self.selected_interfaces)) and self.has_trigger_interface: self.trigger.set()

            # Verifica se o "gatilho" e/ou todas as interfaces dependentes estão prontas
            if (action == "gatilho" and  self.trigger.wait(120)) or ((self.activated_interfaces >= len(self.selected_interfaces)) and not self.has_trigger_interface):
                # Reseta o "gatilho" e o contador de interfaces dependentes
                if self.has_trigger_interface: self.trigger.clear()

                # Aciona o movimento de hoaming nos eixos selecionados.
                if any(self.homing_axis):
                    self.serial.G28(self.homing_axis)

                # Executa o movimento
                await self.apply_coordinates()

    def update_multiple_coordinates(self, payload):
        for k, v in payload.items():
            self.coordinates[k.lower()] = v
        self.activated_interfaces+=1

    async def apply_coordinates(self):
        self.activated_interfaces = 0

        # Calcula adição de movimento relativo
        pre_move = Counter(self.coordinates.copy())
        pre_move.update(Counter(self.special_coordinates.copy()))

        # Separa as coordenadas em tuplas de eixo e valor
        movement = [
            (k, v)
            for k, v in pre_move.items()
            if v is not None
        ]

        # Executa o movimento
        if self.non_blocking:
            # Sem execução bloqueante
            await self.serial.set_position(movement)
            # await self.serial.G0(*movement)
        else:
            # Com execução bloqueante
            await self.serial.set_position_and_wait(movement)
            # await self.serial.GOTO(*movement)

        # Ativa a proxima interface
        self.on("Sucesso", self.serial_id)

    def get_info(**kwargs):
        return {"options": [{'name':s.name, 'id':str(s._id)} for s in SerialManager.get()]}

    def __selected_interfaces(self):
        return [
            {
                name.lower():value 
                for name, value
                in value._to.__dict__.items()
                if name == "name"
            } for value in self.input_connections
        ]