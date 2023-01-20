# -*- coding: utf-8 -*-
from .object.object import Manager, Object
import re

class Option:

    class bind:
        def __init__(self, initial,  obj, key):
            self.obj = obj
            self.key = key
            self.initial = initial

        def get(self):
            return self.obj[self.key]

        def set(self, value):
            self.obj[self.key] = value

    def __init__(self, descritor):
        self.__dict__['properties'] = {}                #! Avoid recursion
        self.update(descritor)
        
    def update(self, descritor):
        self.properties.update(
            {
                key: Option.bind(
                    *self.parser(value)
                ) if isinstance(value, str) and value.startswith("$") else value
                for key, value in descritor.items()
            }
        )

    def __getattr__(self, name):
        value = self.properties[name]
        if isinstance(value, Option.bind):
            return value.get()
        return value

    def __setattr__(self, name, value):
        if isinstance(self.properties[name], Option.bind):
            self.properties[name].set(value)
        else:
            self.properties[name] = value
    
    def __getitem__(self, name):
        return self.__getattr__(name)

    def __setitem__(self, name, value):
        self.__setattr__(name, value)

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
                try:
                    obj = Manager.get_by_name(match.group('name')) or Object(**Manager.get_item(query={'content.name': match.group('name')}, user=Manager.user))
                    if obj:
                        return getattr(obj, match.group('prop')), obj, match.group('prop')
                except TypeError:
                    # Manager.get_item() return None, ** will fail.
                    pass
            return None, None, None
        raise ValueError("Invalid string format, it should be '${0}', but it was '{1}'".format(
            "{object_name.prop}", string))
    