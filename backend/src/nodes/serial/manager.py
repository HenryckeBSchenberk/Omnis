from uuid import uuid4

def get_id(payload):
    _id = str(getattr(payload, '_id', uuid4().hex))
    payload._id = _id
    return _id

class Serial_Manager():
    def __init__(self) -> None:
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
        return self.store.get(str(_id), None)

Manager = Serial_Manager()