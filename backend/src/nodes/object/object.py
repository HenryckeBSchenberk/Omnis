from bson import ObjectId as new_id

from .manager import Manager

class Object:
    def __init__(self, content={}, _id=None):
        self.__dict__['_id'] = new_id(_id)          # Create new id if not exist
        
        if  self._id not in Manager.store:          # IF not exist, create new content and add to manager.
            for key, value in content.items():
                self.__dict__[key] = value
            Manager.add(self)
        else:                                       # IF an object with same id exist, get the content and update it.
            self.__update(content)


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
        return Manager.get_by_id(self._id).__dict__.get(name, None)

    def __set(self, name, value):
        # Get from mamaner the object with same id and set the content
        Manager.get_by_id(self._id).__dict__[name] = value

    def load(self, data):
        self.__update(data)
    
    def export(self):
        return {'_id': self._id, **self.__dict__}

    def __update(self,content):
         for key, value in content.items():
                Manager.get_by_id(self._id).__dict__[key] = value
        #  Manager.get_by_id(self._id).__dict__['content'].update(content)

    def __str__(self):
        return str(self.export())

    def __repr__(self):
        return self.__str__()
        