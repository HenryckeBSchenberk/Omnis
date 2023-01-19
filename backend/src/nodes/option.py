# -*- coding: utf-8 -*-
from .object.object import Manager


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
                    *Manager.parser(value)
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
