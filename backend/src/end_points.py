from datetime import datetime
from src.nodes.node_manager import NodeManager
from starlette.responses import StreamingResponse, JSONResponse
from os.path import abspath
from cv2 import imread, imencode
from src.manager.camera_manager import CameraManager
#! BREAKING CHANGES -- START
# import simplejpeg 
# from vidgear.gears.asyncio.helper import reducer
#! BREAKING CHANGES -- END
import asyncio
from api import logger
from starlette.endpoints import WebSocketEndpoint
from bson import ObjectId

failpath = abspath("./src/imgs/no_image.jpg")

#! BREAKING CHANGES -- START
# def encode(frame):
#     return simplejpeg.encode_jpeg(frame, colorspace="BGR", quality=90, fastdct=True) 


# async def frame_producer(_id="default"):
#     while True:
#         yield (
#             b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n"
#             + imencode(".jpg", await reducer(CameraManager.read(_id), percentage=75))[
#                 1
#             ].tobytes()
#             + b"\r\n"
#         )
#         await asyncio.sleep(0.00001)


# async def custom_video_response(scope):
#     """
#     Return a async video streaming response for `frame_producer2` generator
#     """
#     assert scope["type"] in ["http", "https"]
#     await asyncio.sleep(0.00001)
#     return StreamingResponse(
#         frame_producer(scope.path_params.get("video_id", "default")),
#         media_type="multipart/x-mixed-replace; boundary=frame",
#     )
#! BREAKING CHANGES -- END
async def health(*args):
    return JSONResponse({'success': True, 'message': "It is working" })

class Echo(WebSocketEndpoint):
    encoding = "json"
    _id = None

    async def on_connect(self, websocket):
        await websocket.accept()

    async def on_receive(self, websocket, data):
        node_id = data.get("nodeId")
        if node_id:
            running_node = NodeManager.getNodeById(node_id)
            if running_node:
                running_node.update_options(data["options"])
        await websocket.send_json({"echo": data["options"]})

    async def on_disconnect(self, websocket, close_code=100):
        print("disconnected")



class Websocket(WebSocketEndpoint):
    encoding = "json"
    _id = ObjectId()
    connections = {}

    def __init__(self, _id, updated_info):
        self._id = _id
        self.updated_info = updated_info

    def __call__(self, scope, receive, send):
        super().__init__(scope, receive, send)
        return self

    async def on_connect(self, websocket):
        await websocket.accept()
        if self.connections.get(self._id) is not None:
            self.connections[self._id].add(websocket)
        else:
            self.connections[self._id] = set([websocket])
        await asyncio.sleep(0.5)
        await self._broadcast(self.parser(self.updated_info))

    async def on_receive(self, websocket, data):
        await websocket.send_json({"response": "pong"})

    async def on_disconnect(self, websocket, close_code=100):
        self.connections.get(self._id, set()).remove(websocket)
        logger.debug(
            f"[{self._id}]: {len(self.connections.get(self._id))} remaining sessions"
        )

    async def _broadcast(self, payload: dict):
        for client in list(self.connections.get(self._id, [])):
            await self.send_to_client(client, payload)

    async def send_to_client(self, client, payload: dict):
        try:
            # logger.info(f"send for {len(list(self.connections.get(self._id, [])))} clients")
            await client.send_json(payload)
        except (RuntimeError, AttributeError):
            logger.warning('Fail to send message on websocket.')
            await self.on_disconnect(client, -5)

    async def broadcast_on_change(self, updated_info, payload={}, **kwargs):
        # updated_info = getattr(updated_info_pointer, kwargs.get('attr', '__undefined_attr'), updated_info_pointer)
        old_status = self.parser(updated_info).copy()
        while True:
            
            if self.parser(updated_info) != old_status:
                old_status = self.parser(updated_info).copy()
                await self._broadcast(self.parser(payload))
                await asyncio.sleep(float(kwargs.get('ms', 0.03))) #3ms
                # await asyncio.sleep(0.01)
            await asyncio.sleep(0.03)
    def parser(self, info):
        return info if not callable(info) else info()


class Connection(Websocket):
    def __init__(self) -> None:
        self._id = "network_status"
        super().__init__("network_status", lambda: True)

    async def on_receive(self, websocket, data):
        cons = {str(k):len(v) for k, v in self.connections.items()}
        await self._broadcast({"pong":datetime.utcnow().timestamp(), "connections":cons if cons else "nothing"})

class NodeStatus(Websocket):
    def __init__(self, _id, updated_info):
        super().__init__(_id, updated_info)

class Process(Websocket):
    def __init__(self, _id, process):
        super().__init__(_id, process)
    
    async def on_receive(self, websocket, data):
        await super().on_receive(websocket, data)
        await self._broadcast()

class Controls(Websocket):
    def __init__(self, _id, serial):
        super().__init__(_id, serial.status)
        self.serial = serial

    # async def _broadcast(self, *args):
    #     await super()._broadcast(self.serial.status)

    async def on_receive(self, websocket, data):
        if data["context"] == "movementScale":
            # Define a escala de movimento
            for axis in self.serial.axes.values():
                axis.step = float(data["value"])

        elif data["context"] == "joggingDistance":
            # Move a distancia especificada
            axis = self.serial.axes[data["id"]]
            axis.move(float(data["value"]))
            axis.position = self.serial.G0(*axis())[axis.name]

        elif data["context"] == "outputDevices":
            # Ativa ou desativa os dispositivos de saida
            self.serial.send(self.serial.pins[data["id"]].set_value(data["pwm"]))

        elif data["context"] == "joggingStep":
            # Movimento "Relativo"
            axis = self.serial.axes[data["id"]]
            axis.move(axis.position + axis.step * (1 if not data["isNegative"] else -1))
            axis.position = self.serial.G0(*axis())[axis.name]
        elif data["context"] == "contextMenuCommand":
            # Executa um comando do menu
            logger.info("Executing command: {}".format(data["command"]))
            self.serial.send(data["command"])
        elif data["context"] == "macroAction":
            # Executa uma macro
            logger.info("Executing macro: {}".format(data["value"]))
            self.serial.send(data["value"])
        else:
            logger.debug(f"Websocket: unknow request {data}")

        await websocket.send_json({"respose": "ok"})
