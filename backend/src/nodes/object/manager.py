from bson import ObjectId as new_id
from src.crud import CRUD


def get_id(payload):
    _id = new_id(getattr(payload, '_id', None))
    if payload._id is None:
        payload._id = _id
    return _id


class Object_Manager(CRUD):
    def __init__(self) -> None:
        CRUD.__init__(self, "object", None)
        self.store = {}

    def add(self, payload):
        _id = get_id(payload)
        self.store[_id] = payload

    def get(self):
        return list(self.store.values())

    def add_device(self, device):
        self.add(device)

    def remove_by_id(self, _id):
        return self.store.pop(_id, None)

    def remove(self, payload):
        _id = get_id(payload)
        return self.remove_by_id(_id)

    def get_by_id(self, _id):
        return self.store.get(new_id(_id), None)


Manager = Object_Manager()
