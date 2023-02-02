import functools
from src.nodes.alerts.alert_obj import Alert
from src.message import Message
from src.nodes.node_manager import NodeManager
from src.nodes.option import Option
from api import logger, exception
from api.store import nodes
from api.subscriptions import SubscriptionFactory
from threading import Event
from threading import Thread, Event
import asyncio
import queue
event_list = queue.Queue()

from src.manager.process_manager import ProcessManager as process
from src.user import User

NODE_TYPE = "BASE_NODE"
rtc_status = SubscriptionFactory(nodes, "nodes")

class Observer(object):
    def fail(exteral_execution):
        def wrapper(self, message):
            try:
                exteral_execution(self, message)
            except Exception as e:
                Alert("error", "Falha durante o processo", "Erro: {}".format(str(e)))
                process.stop(user=User('omnis', 'bot', 'developer', 'parallax@orakolo.com'))
                raise
        return wrapper

    fail = staticmethod(fail)

from api.websocket import ConnectionManager

class Node_Websocket_API(ConnectionManager):
    def __init__(self, _id=None):
        super().__init__(_id)


class BaseNode(Observer):
    websocket_route = Node_Websocket_API()
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

    def __init__(self, name, type_, id, options, output_connections, obj=None) -> None:
        self.loop = asyncio.get_event_loop()
        self.name = name
        self.type = type_
        self._id = id
        self.options = Option(options, obj)
        self.output_connections = {item._from.name: item for item in output_connections }
        self.running = True
        self.stop_event = Event()
        self.auto_run = options.get("auto_run", False)
        self.user = User('omnis', 'node_executor', 'developer', '')
        logger.debug(f"[{type(self).__name__}] || {self.name} Node loaded")

    def Notify_Execution(payload_before={}, payload_after={}):
        """
        Broadcasts a message to the websocket route before and after the execution of a node.
        the message will be updated with the node's information and the running status.
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(self, message):
                
                payload_before.update({**self.info(), 'running': True})
                await self.websocket_route.broadcast(payload_before)
                
                await func(self, message)

                payload_after.update({**self.info(), 'running': False})
                await self.websocket_route.broadcast(payload_after)

            return wrapper
        return decorator
        

    def onSuccess(self, payload, additional=None):
        self.on("onSuccess", payload, additional)

    def onSignal(self, signal=True):
        self.on("Sinal", signal)

    def onFailure(self, payload, additional=None, pulse=True, errorMessage=""):
        self.on("onFailure", payload, additional, pulse)

    def on(self, trigger, payload, additional=None, pulse=False, errorMessage=""):
        logger.debug(f'[{self.name}] || interface {trigger} requested')
        target = self.output_connections.get(trigger, None)
        logger.debug(f'[{self.name}] || connection {target} selected')
        if target is not None:
            message = Message(
                target._from.id,
                target._to.id,
                target._from.name,
                target._to.name,
                target._from.nodeId,
                target._to.nodeId,
                payload,
                additional,
            )
            logger.debug(f'[{self.name}] || using message: {message} ')
            node_to_run = NodeManager.getNodeById(target._to.nodeId)
            if node_to_run is not None:
                logger.debug(f'[{self.name}] || Resquest tasking on node: {node_to_run} ')

                self.loop.create_task(
                    self.websocket_route.broadcast(
                        {
                            'connection': {
                                'from': target._from.id,
                                'to': target._to.id
                            }
                        }
                    )
                )
                
                self.loop.create_task(node_to_run.execute(message))
            else:
                logger.error(f"[{self.name}] || Can't find node {target._to.nodeId}")
                raise IndexError(f"Can't find node {target._to.nodeId}")
        else:
            logger.warning(
                f"Node {self.name} has no output connection for trigger {trigger}"
            )

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
        self.loop.create_task(self.execute(message))

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

    def info(self):
        return {
            "name": self.name,
            "id": self._id,
        }

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def normalize_id_on_dict(dictionary):
        temp = dictionary.copy()
        temp["_id"] = str(dictionary["_id"])
        return temp