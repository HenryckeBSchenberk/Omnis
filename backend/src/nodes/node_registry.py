"""
scan all folders in 'src.nodes' and import all modules using this pattern:
from src.nodes.[node_name_folder].[node_name] import [NodeName] ( node_name package must finish with '_node.py' )
"""
from os import listdir
import importlib
from api import logger, exception
from api.decorators import for_all_methods


class RegEntry:
    """
    name: name of the node
    clss: class of the node
    """

    def __init__(self, name, clss):
        self.name = name
        self.clss = clss


@for_all_methods(exception(logger))
class NodeRegistry:
    @staticmethod
    def getNodeClassByName(name):
        """
        :param name: name of the node, e.g. 'identify'
        :return: class of the node, e.g. IdentifyNode
        """

        for entry in nodeRegistry:
            if entry.name == name:
                return entry.clss
        else:
            raise Exception("Class " + str(name) + " not registered")


package_nodes = []  # list of package names and classes
nodeRegistry = []   # list of RegEntry objects created from package_nodes

# Use map() and filter() to filter out all the files that end with .py or start with _ in the list '_all'
for _dir in list(
    filter(lambda x: not (x[-3:] == ".py" or x[0] == "_"), listdir("src/nodes"))
):
    # Store all nodes in a dictionary list 'package_nodes', {package_name, class_name}
    list(
        map(
            lambda x: package_nodes.append(
                {
                    "package_name": f".{_dir}.{x[:-3]}",
                    "class_name": f"{x[0].upper()}{x[1:-8]}Node",
                    "graphql": f"{_dir}.graphql"# if file_exists(f"{_dir}.graphql")  else False
                }
            ),
            filter(lambda x: x[-8:] == "_node.py", listdir(f"src/nodes/{_dir}")),
        )
    )

# import all the nodes in the list 'package_nodes',
# and store them in the list 'nodeRegistry' using the RegEntry class

for mod in package_nodes:
    mod["package_name"] = importlib.import_module(mod["package_name"], __package__)
    nodeRegistry.append(
        RegEntry(
            getattr(mod["package_name"], "NODE_TYPE"),
            getattr(mod["package_name"], mod["class_name"]),
        )
    )

from src.nodes.object.manager import Manager as ObjectManager
from src.nodes.variable.variable import __variable
from src.nodes.sketch.sketch import __sketch
from src.nodes.levels.levels import __levels