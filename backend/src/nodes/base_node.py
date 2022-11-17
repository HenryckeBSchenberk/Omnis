from src.nodes.alerts.alert_obj import Alert
from src.message import Message
from src.nodes.node_manager import NodeManager
from api import logger, exception
from api.decorators import for_all_methods
from api.store import nodes
from api.subscriptions import SubscriptionFactory
from threading import Event
from threading import Thread, Event
import asyncio
import queue
event_list = queue.Queue()

from src.manager.process_manager import ProcessManager as process
from src.utility.crud.user import User

NODE_TYPE = "BASE_NODE"
rtc_status = SubscriptionFactory(nodes, "nodes")

class Wizard(object):
    def _decorator(exteral_execution):
        def magic(self, message):
            try:
                exteral_execution(self, message)
                event_list.get()
            except Exception as e:
                Alert("error", "Falha durante o processo", "Erro: {}".format(e))
                process.stop(user=User('omnis', 'bot', 'developer', 'parallax@orakolo.com'))
                raise e
            finally:
                event_list.task_done()
        return magic

    _decorator = staticmethod(_decorator)

    # @_decorator
    # def execute(self):
    #     logger.error("The Wizard decorator should decorate an node 'execute' function.")

    # _decorator = staticmethod(_decorator)

class BaseNode(Wizard):
    """
    A class that represents a node, and its properties.

    Attributes:
        name (str): The name of the node.
        type (str): The type of the node.
        id (str): The id of the node.
        options (dict): The options of the node.
        output_connections (list): The output connections of the node.

    Methods:
        onSuccess(payload, additional): Sends a success message to the node.
        onSignal(signal): Sends a signal message to the node.
        onFailure(payload, additional): Sends a failure message to the node.
        on(trigger, payload, additional): Sends a message to the node.
        pause(): Pauses the node.
        resume(): Resumes the node.
        stop(): Stops the node.
        reset(): Resets the node.
        pulse(color): Pulses the node.
        sendConnectionExec(fromId, toId):
        Sends a connection execution message to the node.
        sendErrorMessage(nodeId, errorMessage): Sends an error message to the node.

    """

    def __init__(self, name, type_, id, options, output_connections) -> None:
        self.loop = asyncio.get_event_loop()
        self.name = name
        self.type = type_
        self._id = id
        self.options = options
        self.output_connections = output_connections
        self.running = True
        self.stop_event = Event()
        self.auto_run = options.get("auto_run", False)
        logger.debug(f"[{type(self).__name__}] || {self.name} Node loaded")

    def onSuccess(self, payload, additional=None):
        self.on("onSuccess", payload, additional)

    def onSignal(self, signal=True):
        self.on("Sinal", signal)

    def onFailure(self, payload, additional=None, pulse=True, errorMessage=""):
        self.on("onFailure", payload, additional, pulse)

    def on(self, trigger, payload, additional=None, pulse=False, errorMessage=""):
        for target in list(
            filter(
                lambda connection: connection.get("from").get("name") == trigger,
                self.output_connections,
            )
        ):

            message = Message(
                target.get("from").get("id"),
                target.get("to").get("id"),
                target.get("from").get("name"),
                target.get("to").get("name"),
                target.get("from").get("nodeId"),
                target.get("to").get("nodeId"),
                payload,
                additional,
            )

            node_to_run = NodeManager.getNodeById(target.get("to").get("nodeId"))
            self.loop.create_task(node_to_run.execute(message))

    def AutoRun(self):
        message = Message(
            "auto_run",
            "auto_run",
            "auto_run",
            "auto_run",
            "auto_run",
            "auto_run",
            "auto_run",
        )
        self.reset()
        self.execute(message)

    def pause(self):
        self.running = False
        return True

    def resume(self):
        self.running = True
        self.stop_event.clear()
        return True

    def stop(self):
        self.stop_event.set()

    def reset(self):
        self.stop()
        self.stop_event.clear()
        self.running = True

    # Todo: Implement the following methods in the frontend0
    def pulse(self, color):
        return {"NodeId": self._id, "color": color}

    def sendConnectionExec(self, fromId, toId):
        return {"type": "CONNECTION_EXEC", "data": {"from": fromId, "to": toId}}

    def sendErrorMessage(self, nodeId, errorMessage):
        return {
            "type": "NODE_EXEC_ERROR",
            "data": {"nodeId": nodeId, "errorMessage": errorMessage},
        }

    def __str__(self) -> str:
        return f"[{self.type}|{self.name}]"

    def to_dict(self):
        return {
            "name": self.name,
            "id": self._id,
            "options": self.options,
            "output_connections": self.output_connections,
        }

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def normalize_id_on_dict(dictionary):
        temp = dictionary.copy()
        temp["_id"] = str(dictionary["_id"])
        return temp