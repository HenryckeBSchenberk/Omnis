class Connection:
    
    OPEN = 'Opened'
    CLOSED = 'Closed'

    def __init__(self, _id, name, description, initial_status):
        super().__init__()
        self._id = _id
        self.name = name
        self.description = description
        self.status = initial_status

    def open(self):
        self.status = Connection.OPEN
    
    def close(self):
        self.status = Connection.CLOSED

    def __str__(self):
        return f'Connection: {self.name} | {self.description} | {self.status}'

class Process:
    
    START = 'Running'
    STOP = 'Stopped'
    PAUSE = 'Paused'
    RESUME = START

    def __init__(self, _id, name, description, initial_status):
        super().__init__()
        self._id = _id
        self.name = name
        self.description = description
        self.status = initial_status

    def start(self):
        self.status = Process.START
    
    def stop(self):
        self.status = Process.STOP

    def pause(self):
        self.status = Process.PAUSE

    def resume(self):
        self.status = Process.RESUME

    def __str__(self):
        return f'Process: {self.name} | {self.description} | {self.status}'

class Node(Process):

    LOAD = 'Loaded'
    UNLOAD = 'Unloaded'
    ERROR = 'Error'

    def __init__(self, _id, name, description, initial_status):
        super().__init__(_id, name, description, initial_status)
        self._id = _id
        self.name = name
        self.description = description
        self.status = initial_status

    def load(self):
        self.status = Node.LOAD
    
    def unload(self):
        self.status = Node.UNLOAD

    def error(self):
        self.status = Node.ERROR

    def __str__(self):
        return f'Node: {self.name} | {self.description} | {self.status}'
