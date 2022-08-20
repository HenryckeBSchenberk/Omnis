from src.manager.base_manager import BaseManager
from src.crud import SSPR
from api import logger, auth
from api.mutations import mutation

class SerialObjectManager(SSPR, BaseManager):
    def __init__(self, alias, auth_level, collection):
        SSPR.__init__(self, alias=alias, auth_level=auth_level)
        BaseManager.__init__(self)
        
        self.reset = (auth(auth_level))(self.reset)
        mutation.set_field(f"reset_serial", self.reset)

        self.send = (auth(auth_level))(self.send)
        mutation.set_field(f"sendSerial", self.send)
    
    def add(self, *args, **kwargs):
        super().add(*args, **kwargs)
        self.selected_serial_id = kwargs.get('_id')

    def broadCast(self, message):
        for ser in self.store:
            ser.send(message)
    
    def verify_serial(func):
        def wrapper(self, *args, **kwargs):
            if self.serial is None:
                raise TypeError('Serial is not defined')
            return func(self, *args, **kwargs)
        return wrapper

    @verify_serial
    def start(self, **kwargs):
        logger.info(self.serial.name)
        self.serial.start()

    @verify_serial
    def stop(self,  **kwargs):
        self.serial.close()

    @verify_serial
    def reset(self, **kwargs):
        self.serial.close()
        self.serial.start()

    @verify_serial
    def send(self, payload, **kwargs):
        self.serial.send(payload)
        return self.serial.to_dict()

    @verify_serial
    def pause(self,  **kwargs):
        raise TypeError('Invalid Option')
    
    @verify_serial
    def resume(self, **kwargs):
        raise TypeError('Invalid Option')
    
    def select(self, _id, **kwargs):
        self.serial = _id
        return self.serial is not None

    @property
    def serial(self):
        return self.store.get(self.selected_serial_id)

    @serial.setter
    def serial(self, _id):
        self.selected_serial_id = _id

SerialManager = SerialObjectManager('serial', 'operator', 'serial')
