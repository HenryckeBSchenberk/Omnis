# from src.crud import CRUD
# __sketch = CRUD("sketch", "operator")
from src.nodes.manager import Manager as BaseManager, ExecutarNoCrud as sync

class Sketch_Manager(BaseManager):
    def __init__(self):
        super().__init__("sketch", "operator")
    
    @sync('create')
    def create(self, **kwargs):
        pass
    
    @sync('update')
    def update(self, **kwargs):
        pass
    
    @sync('delete')
    def delete(self, **kwargs):
        pass

    @sync('get_item')
    def get_item(self, **kwargs):
        pass
    
    @sync('get_list')
    def get_list(self, **kwargs):
        pass


Manager = Sketch_Manager()
        