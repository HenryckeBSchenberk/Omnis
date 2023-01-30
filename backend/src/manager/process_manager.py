from src.manager.base_manager import BaseManager
from src.nodes.node_manager import NodeManager
from src.crud import SSPR
from src.loader import loadConfig, LoadingMode
from src.nodes.process.process import sample_process as Process
from src.nodes.object.object import Manager as ObjectManager, Object
from src.end_points import Process as WebProcess
from api import logger, dbo, auth
from api.mutations import mutation

from threading import Thread
import asyncio

class ProcessObjectManager(SSPR, BaseManager):
    def __init__(self, alias, auth_level, collection):
        SSPR.__init__(self, alias=alias, auth_level=auth_level, collection=collection)
        BaseManager.__init__(self)
        self._id = "status"
        self.loaded_id = None
        self.selected_process_id = None
        for process in dbo.find_many(self.collection):
            self.add(Process(**process))
            self.selected_process_id = process['_id']
        self.__status = [self.process]
        self.websocket = WebProcess(self._id, self.status)
        Thread(
            target=self.auto_update, name=f"{self._id}_auto_update", daemon=True
        ).start()

        self.load_config = (auth(auth_level))(self.load_config)
        mutation.set_field(f"load_config", self.load_config)

    def auto_update(self):
        asyncio.run(self.websocket.broadcast_on_change(self.status, self.status))

    def start(self, **kwargs):
        self.load(kwargs.get('_id') , kwargs.get('object_id'), kwargs.get('user'))
        self.process.start()

    def stop(self,  **kwargs):
        self.process.stop()

    def pause(self,  **kwargs):
        self.process.pause()
    
    def resume(self, **kwargs):
        self.process.resume()

    def status_generator(self, process):
        def status():
            return process.status
        return status()

    def select(self, _id, **kwargs):
        self.process = _id
        self.__status[0] = self.process

    def __call__(self, process=None):
        if process: self.process = process
        return self.process

    @property
    def process(self):
        atual = self.store.get(self.selected_process_id, False)
        if atual:
            return atual
        else:
            config = dbo.find_one(self.collection, {'_id':self.selected_process_id})
            if config:
                self.add(Process(**config))
                return self.process
            return None
                # raise KeyError("PROCESS NOT FOUND, IF EXIST TRY REBOOT")
    
    @process.setter
    def process(self, _id):
        self.selected_process_id = _id

    def status(self):
        return getattr(self.__status[0], 'status', {'status': 'UNKNOWN'})
    

    def load(self, _id=False, object_id=False, user=None):
        self.unload()
        full_sketch = dbo.find_one('sketch', _id or self.process.sketch.id)

        object_id = object_id or self.process.object.id
        obj = ObjectManager.get_item(_id=object_id, user=user)
        
        loaded = loadConfig(full_sketch['content'], obj)
        if loaded:
            self.loaded_id = self.process.sketch.id if not _id else _id
        else:
            self.loaded_id = None
            self.unload()
        return full_sketch

    def unload(self):
        if self.loaded_id is not None:
            NodeManager.stop()
            NodeManager.clear()
            self.loaded_id = None
            return True
        return False

    def load_config(self, _id, user):
        return self.load(_id)

ProcessManager = ProcessObjectManager('process', 'operator', 'process')