from src.nodes.manager import Manager as BaseManager, ExecutarNoCrud as sync
from numpy import fromiter

class MatrixObjectManager(BaseManager):
    def __init__(self, collection, auth_level):
        super().__init__(collection=collection, auth_level=auth_level)

    @sync('create')
    def create(self, *args, **kwargs): pass

    @sync('get_item')
    def get_item(self, *args, **kwargs): pass

    @sync('get_list')
    def get_list(self, *args, **kwargs): pass

    @sync('update')
    def update(self, *args, **kwargs): pass

    @sync('delete')
    def delete(self, *args, **kwargs): pass

    @sync('dulicate')
    def duplicate(self, *args, **kwargs): pass
MatrixManager = MatrixObjectManager("matrix", "operator")