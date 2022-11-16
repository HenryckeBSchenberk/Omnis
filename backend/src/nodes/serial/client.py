from wspyserial.client import Device
from wspyserial.protocol import package as pkg
from manager import Manager as SM
from os import environ

HOST = environ.get("SERVER_HOST", "0.0.0.0")
PORT = environ.get("SERVER_PORT", 8010)

class CustomSerial(Device):
    def __init__(self, host, port, manager=SM, loop=None):
        super().__init__(f"ws://{host}:{port}", loop=loop)
        self._pins = None
        self._axes = None
        self._manager = manager
        self._manager.add_device(self)
    


if __name__ == "__main__":
    Client = CustomSerial(HOST, PORT)
    import asyncio
    _id = Client._id
    async def main():
        async with SM.get_by_id(_id) as client:
            print(await client.send(pkg("M114", 2)))
    asyncio.run(main())