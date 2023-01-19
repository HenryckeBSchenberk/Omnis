from bson import ObjectId as new_id
from src.crud import CRUD
import re


def get_id(payload):
    _id = new_id(getattr(payload, '_id', None))
    if payload._id is None:
        payload._id = _id
    return _id


class Object_Manager(CRUD):
    def __init__(self) -> None:
        CRUD.__init__(self, "object", 'operator')
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

    def get_by_name(self, name):
        # Storage managers shold be improved with BTrees, or indexes for fast search?.
        for obj in self.store.values():
            if obj.name == name:
                return obj
        return None

    def parser(self, string):
        """
        Parser a payload

        """
        obj = None
        regex_pattern = r"\$\{(?P<name>[\w]+)\.(?P<prop>[\w]+)\}"
        regex = re.compile(regex_pattern)
        if isinstance(string, str) and string.startswith('${') and string.endswith('}'):
            match = regex.search(string)
            if match:
                obj = self.get_by_name(match.group('name'))
                if obj:
                    return getattr(obj, match.group('prop')), obj, match.group('prop')
                return obj, False
            return False, None
        raise ValueError("Invalid string format, it should be '${0}', but it was '{1}'".format(
            "{object_name.prop}", string))


Manager = Object_Manager()
