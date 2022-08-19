from src.manager.base_manager import BaseManager
from src.crud import SSPR
from api import dbo

class SerialObjectManager(SSPR, BaseManager):
    def __init__(self, alias, auth_level, collection):
        SSPR.__init__(self, alias=alias, auth_level=auth_level)
        BaseManager.__init__(self)
        for serial in dbo.find_many(collection, {},{'_id':1}):
            # Serial(**serial)
            self.selected_serial_id = serial

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
        self.serial.start()

    @verify_serial
    def stop(self,  **kwargs):
        self.serial.stop()

    @verify_serial
    def reset(self, **kwargs):
        self.serial.reset()

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
