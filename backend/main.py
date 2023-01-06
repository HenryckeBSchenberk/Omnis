from os import environ
import uvicorn
import socket
from api import logger, dbo
from api.graphql_types import custom_types
from api.queries import query
from api.subscriptions import subscription
from api.mutations import mutation

from src.end_points import Echo
from src.nodes.base_node import BaseNode
from src.nodes.serial import setup as serial_setup
from src.nodes.camera import setup as camera_setup
from src.nodes.serial.manager import Manager as SerialManager
from src.nodes.camera.manager import Manager as CameraManager

from src.manager.process_manager import ProcessManager as process

from ariadne.asgi import GraphQL
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
)

from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount, WebSocketRoute
from starlette.applications import Starlette
from os import listdir
from os.path import exists as file_exists


type_defs = ""
for _file in ["schema", "inputs", "types", "results", "interfaces"]:
    type_defs += load_schema_from_path(f"./src/graphql/{_file}.graphql") + ("\n" * 2)

for _dir in list(
    filter(lambda x: not (x[-3:] == ".py" or x[0] == "_"), listdir("src/nodes"))
):
    if file_exists(f'src/nodes/{_dir}/{_dir}.graphql'):
        type_defs += load_schema_from_path(f'src/nodes/{_dir}/{_dir}.graphql') + ("\n" * 2)

schema = make_executable_schema(
    type_defs, query, mutation, subscription, snake_case_fallback_resolvers, *custom_types 
)


serial_setup()
camera_setup()


routes_app = [
    #! BREAKING CHANGES - START
    # Route(
    #     "/videos/{video_id}", endpoint=custom_video_response, methods=["GET", "POST"]
    # ),
    # Route("/health",  endpoint=health,  methods=["GET", "POST"]),
    # WebSocketRoute("/ws", endpoint=Echo),
    # WebSocketRoute("/network", endpoint=Connection()),
    WebSocketRoute("/process", endpoint=process.websocket),
    # WebSocketRoute("/nodes", endpoint=Echo),
    *[WebSocketRoute(f"/serial/{device._id}", endpoint=device.webscoket_route) for device in SerialManager.get()],
    *[WebSocketRoute(f"/camera/{device._id}", endpoint=device.webscoket_route) for device in CameraManager.get()],
    WebSocketRoute(f"/controls/6244b0ad3a8338aceae46cf1", endpoint=Echo), #! BREAKING CHANGES
    WebSocketRoute(f"/nodes", endpoint=BaseNode.websocket_route), #! BREAKING CHANGES
    #! BREAKING CHANGES - END
    Mount(
        "/",
        app=CORSMiddleware(
            GraphQL(schema, debug=True),
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    )
]

app = Starlette(debug=True, routes=routes_app, on_shutdown=[dbo.close])

port = environ.get("SERVER_PORT", 80)
if environ.get("NODE_ENV") == "development":
    socketI = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketI.connect(("8.8.8.8", 80))
    host = socketI.getsockname()[0]
    socketI.close()
else:
    host = "0.0.0.0"

if __name__ == "__main__":
    try:
        uvicorn.run(app=app, host=host, port=int(port), log_level=logger.level)
    finally:
        dbo.close()
