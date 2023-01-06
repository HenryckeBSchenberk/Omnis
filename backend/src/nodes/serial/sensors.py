from datetime import datetime, timedelta
from uuid import uuid4

class Sensor:
    def __init__(self, name, type, status, _id=None):
        self._id = _id or uuid4().hex
        self.name = name
        self.type = type
        self.status = status
        self.__expire_trusted = datetime.utcnow()

    @property
    def trusted(self):
        return self.__expire_trusted >= datetime.utcnow()
    
    @trusted.setter
    def trusted (self, minutes):
        self.__expire_trusted = datetime.utcnow()+timedelta(minutes=minutes)
        return self.trusted

    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, value):
        self.__status = value
        self.trusted = 10

    def __str__(self) -> str:
        return f'[{self.trusted}] {self.name}_{self.type}: {self.status}'
    
    def __repr__(self) -> str:
        return self.__str__()