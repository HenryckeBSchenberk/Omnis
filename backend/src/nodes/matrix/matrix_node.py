from src.nodes.alerts.alert_obj import Alert
from src.nodes.base_node import BaseNode, Observer
from src.nodes.node_manager import NodeManager
from src.nodes.matrix.matrix_obj import Blister, Slot
from bson import ObjectId
from api import logger, exception, dbo
from api.decorators import for_all_methods
import numpy as np

NODE_TYPE = "MatrixNode"

"""
            [
            "matrix",
            {
              "id": "6256d313daaa135378e4cb27",
              "name": "Blister_0",
              "slots": {
                "qtd": {
                  "X": 5,
                  "Y": 10
                },
                "margin": {
                  "X": 3,
                  "Y": 3
                },
                "size": {
                  "X": 41,
                  "Y": 24
                }
              },
              "subdivisions": {
                "qtd": {
                  "X": 1,
                  "Y": 1
                },
                "margin": {
                  "X": 0,
                  "Y": 0
                }
              }
            }
          ],

          {

  "shape": [
    slot['qtd'][x-y
    ] * subdivisions['qtd'][x->y],
  ],
  "slot_config": {
    "sizes": [
      slot['size'][x-y],
    ],
    "borders": [
        slot['margin'][x-y],
    ],
    "origin": [
        ??? 800,
        ??? 200
    ]
    "counter": [
      config[shape][x-y]/slot['qtd'][x-y],
    ],
    "extra": [
      subdvision['margin'][x-y],
    ]
    ]
  },
          }
"""


def convert_to_array(dict_, type_=float):
    return np.fromiter(dict_.values(), dtype=type_)


@for_all_methods(exception(logger))
class MatrixNode(BaseNode):
    """
    Inputs:
        matrix - Receives a matrix of data.
        next - iterate through the matrix.
    Outputs:
        Slot - A slot that contains the data.
        End - The end of the matrix.

    """

    def __init__(self, name, id, options, output_connections, input_connections, default_object=None):
        super().__init__(name, NODE_TYPE, id, options, output_connections, default_object)
        self.input_connections = input_connections

        slots = options["matrix"]["slots"]
        subdivisions = options["matrix"]["subdivisions"]
        shape = convert_to_array(slots["qtd"], int) * convert_to_array(
            subdivisions["qtd"], int
        )
        slot_config = {
            "sizes": convert_to_array(slots["size"]),
            "borders": convert_to_array(slots["margin"]),
            "origin": convert_to_array(options["matrix"]["origin"]),
            "counter": convert_to_array(slots["qtd"], int),
            "extra": convert_to_array(subdivisions["margin"]),
            "scale": float(options["matrix"]["scale"]),
        }
        # self.blister = Blister(shape=shape, name=options["matrix"]["name"], _id=options["matrix"]["id"],  slot_config=slot_config, order=options["matrix"]["order"])
        try:
            self.blister = Blister(
                **dbo.find_one(
                    "matrix-manager", {"_id": ObjectId(options["matrix"]["id"])}
                )
            )

        except TypeError:
            TypeError(Alert(
                "error",
                "Configuração inválida",
                "O nó de 'matrix' não foi capaz de ser criado com as configurações definidas.",
                f"Verifique as matrizes disponíveis e reconfigure o nó {self._id}.",
                delay=0.1
            ).items())
        self.auto_run = options.get("auto_run", False)
        NodeManager.addNode(self)

    #@Observer.fail
    def execute(self, message):
        target = message.targetName.lower()
        match target:
            case "reset":
                if isinstance(message.payload, Blister):
                    self.blister.update_data(message.payload.data)
                self.reset()
                self.item()

            case "próximo":
                return self.item()

            case "imagem":
                self.on("Matriz", self.blister.roi(message.payload))

    def item(self):
        _ = next(self.blister)
        if not self.blister.empty.is_set():
            item = _[1]
            logger.debug(f'item index: {_[0]}')
            self.on(
                "Item", item
            )  # Send only the slot. Maybe another node is required to split item and slot data.
            self.on(
                "XY", dict(zip(["X", "Y"], item.center))
            )  #! Thats is not the best option ...
        else:
            self.on("Fim", True)
            # self.reset()

    def reset(self):
        self.blister.reset_iterator()

    @staticmethod
    def get_info(**kwargs):
        return {
            "options": list(
                map(
                    MatrixNode.normalize_blister_get_info,
                    dbo.find_many("matrix-manager", {}),
                )
            ),
        }

    @staticmethod
    def normalize_blister_get_info(blister):
        def set_X_Y(list_, sas=["x", "y"]):
            return dict(zip(sas, list_))

        def verify(divisor):
            if divisor[1] == 0:
                return 1
            return np.array(blister["shape"])[divisor[0]] / divisor[1]

        sub = np.array(list(map(verify, enumerate(blister["slot_config"]["counter"]))))

        return {
            "id": str(blister["_id"]),
            "name": blister["name"],
            "order": blister.get("order", "TLR"),
            "slots": {
                "qtd": set_X_Y((np.array(blister["shape"]) / sub).astype(int).tolist()),
                "margin": set_X_Y(blister["slot_config"]["borders"]),
                "size": set_X_Y(blister["slot_config"]["sizes"][:2]),
            },
            "subdivisions": {
                "qtd": set_X_Y(sub.astype(int).tolist()),
                "margin": set_X_Y(blister["slot_config"]["extra"]),
            },
            "origin": set_X_Y(blister["slot_config"]["origin"][:2]),
            "scale": blister["slot_config"]["scale"],
        }


if __name__ == "__main__":
    S2 = Slot(
        [6, 5, 0],
        [87.08, 80.68, 0],
        [23, 23, 0],
        [42.54, 19.5, 0],
        counter=[5, 3, 2],
        extra=[92.54, 93, 0],
        item="X",
    )

    print(vars(Blister(shape=[6, 6, 0], slot_config=S2)))
