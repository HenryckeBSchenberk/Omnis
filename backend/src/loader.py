from enum import Enum
from datetime import datetime

from .nodes.node_manager import NodeManager
from .nodes.node_registry import NodeRegistry
from .nodes.alerts.alert_obj import Alert
from api import logger, exception, dbo

class LoadingMode(Enum):
    STARTUP = "STARTUP"
    RUNNING = "RUNNING"


class NodeChangeType(Enum):
    # Create, Modify, Delete
    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"


class NodeChange(object):
    # nodeId, nodeName, type, optionsOld, optionsNew, date
    def __init__(self, nodeId, nodeName, nodeType, optionsOld, optionsNew, date):
        self.nodeId = nodeId
        self.nodeName = nodeName
        self.nodeType = nodeType
        self.optionsOld = optionsOld
        self.optionsNew = optionsNew
        self.date = datetime.now()


@exception(logger)
def getNodeByInterfaceId(nodeConfig, interfaceId):
    for n in nodeConfig.get("nodes"):
        for i in n.get("interfaces"):
            if i[1]["id"] == interfaceId:
                return n


@exception(logger)
def getInterfaceByInterfaceId(nodeConfig, interfaceId):
    for id, node in enumerate(nodeConfig.get("nodes")):
        # get first occurrence of interfaceId in node.get("interfaces")
        interface = None
        for i in node.get("interfaces"):
            if i[1]["id"] == interfaceId:
                interface = i
                break

        if interface:
            data = {"id": interface[1].get("id"), "name": interface[0]}
            return data
    return None

@exception(logger)
def extractOptionsFromNode(node):
    node_options = node.get("options")
    options = {}
    for option in node_options:
            options[option[0].lower()] = option[1]
    return options

class Interface:
    def __init__(self, name, id, nodeId):
        self.name = name
        self.id = id
        self.nodeId = nodeId
    
    def __str__(self) -> str:
        return f"Interface({self.name}, {self.id})"
    
    def __repr__(self) -> str:
        return self.__str__()

class Connection:
    def __init__(self, fromInterface, toInterface):
        self._from = fromInterface
        self._to = toInterface
    
    def __str__(self) -> str:
        return f"Connection({self._from} -> {self._to})"
    
    def __repr__(self) -> str:
        return self.__str__()

def extractConnections(nodeConfig):
    connections = nodeConfig.get("connections")
    for connection in connections:
        _from = getInterfaceByInterfaceId(nodeConfig, connection.get("from"))
        _node = getNodeByInterfaceId(nodeConfig, connection.get("from"))

        fromInterface = Interface(
           _from.get("name"),
           _from.get("id"),
           _node.get("id")
        )
        _to = getInterfaceByInterfaceId(nodeConfig, connection.get("to"))
        _node = getNodeByInterfaceId(nodeConfig, connection.get("to"))
        toInterface = Interface(
            _to.get("name"),
            _to.get("id"),
            _node.get("id")
        )
        yield Connection(fromInterface, toInterface)

@exception(logger)
def cleanNodeManager(nodeConfigs):
    configNodeIds = map(
        lambda nodeConfig: None
        if not nodeConfig
        else map(lambda node: node.get("id"), nodeConfig),
        nodeConfigs,
    )
    configNodeIds = [
        item for sublist in configNodeIds for item in sublist
    ]  # flatten list

    runningNodeIds = map(lambda node: node.get("id"), NodeManager.getActiveNodes())
    # Getting deleted nodeIds by creating delta between the two arrays
    deleted = list(set(runningNodeIds) - set(configNodeIds))

    for nodeId in deleted:
        node = NodeManager.getNodeById(nodeId)
        saveNodeChange(
            NodeChange(
                node.get("id"),
                node.get("name"),
                NodeChangeType.DELETE,
                node.get("options")["settings"],
                {},
            )
        )
        NodeManager.resetNode(nodeId)

    return len(deleted)


@exception(logger)
def loadConfig(NodeSheet, obj=None, mode=LoadingMode):
    numberOfNodesTotal = 0
    numberOfNodesChanged = 0
    numberOfNodesInit = 0
    nodesChanged = []
    connectionList = list(extractConnections(NodeSheet))
    for node in NodeSheet.get("nodes"):
        newCls = NodeRegistry.getNodeClassByName(node.get("type"))

        options = extractOptionsFromNode(node)
        existingNode = NodeManager.getNodeById(node.get("id"))

        output_connections = list(
            filter(
                lambda connection: connection._from.nodeId
                == node.get("id"),
                connectionList,
            )
        )
        input_connections = list(
            filter(
                lambda connection: connection._to.nodeId
                == node.get("id"),
                connectionList,
            )
        )

        if existingNode is None:
            try:
                newCls(
                    node.get("name"),
                    node.get("id"),
                    options,
                    output_connections,
                    input_connections,
                    obj,
                )
                numberOfNodesInit += 1
                if mode == LoadingMode.RUNNING:
                    saveNodeChange(
                        NodeChange(
                            node.get("id"),
                            node.get("name"),
                            NodeChangeType.CREATE,
                            {},
                            options.get("settings"),
                        )
                    )
            except Exception as e:
                Alert(
                    "error",
                    "Configuração Inválida",
                    'Não foi possível criar o nó "{}"'.format(
                        node.get("name")
                    ),
                    how_to_solve="Verifique se todos os valores obrigatórios estão presentes",
                )
                raise
        else:
            logger.warning("Node {} EXIST!".format(node.get("name")))
            nodeSettingsChanged = existingNode.options.get(
                "settings"
            ) != options.get("settings")
            outputChanged = existingNode.output_connections != output_connections
            nameChanged = existingNode.name != node.get("name")

            inputChanged = (
                existingNode.input_connections is not None
                and existingNode.input_connections != input_connections
            )

            if existingNode and (
                nodeSettingsChanged or outputChanged or inputChanged or nameChanged
            ):
                numberOfNodesChanged += 1
                nodesChanged.append(node.get("name"))

                if nodeSettingsChanged:
                    saveNodeChange(
                        NodeChange(
                            node.get("id"),
                            node.get("name"),
                            NodeChangeType.MODIFY,
                            existingNode.options.get("settings"),
                            options.get("settings"),
                        )
                    )

    numberOfNodesTotal += len(NodeSheet.get("nodes"))

    return NodeSheet
@exception(logger)
def saveNodeChange(nodeChange):
    dbo.get_collection("node-history").insert_one(nodeChange)
