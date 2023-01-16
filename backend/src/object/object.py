from uuid import uuid4

from .manager import Manager

class Object:
    def __init__(self, content={}, _id=None):
        self.__dict__['_id'] = _id or uuid4().hex
        
        if  self._id not in Manager.store:          # IF not exist, create new content and add to manager.
            self.__dict__['content'] = content
            Manager.add(self)
        else:                                       # IF an object with same id exist, get the content and update it.
            Manager.get_by_id(self._id).__dict__['content'].update(content)


    def __getattr__(self, name):
        return self.__get(name)

    def __setattr__(self, name, value):
        self.__set(name, value)

    def __setitem__(self, name, value):
        self.__set(name, value)
    
    def __getitem__(self, name):
        return self.__get(name)

    def __get(self, name):
        # Get from mamaner the object with same id and get the content
        return Manager.get_by_id(self._id).__dict__['content'].get(name, None)

    def __set(self, name, value):
        # Get from mamaner the object with same id and set the content
        Manager.get_by_id(self._id).__dict__['content'][name] = value
