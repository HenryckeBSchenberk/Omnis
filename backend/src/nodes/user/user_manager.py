from src.nodes.manager import Manager as BaseManager, ExecutarNoCrud as sync
from src.user import User

class User_Manager(BaseManager):
    def __init__(self):
        super().__init__("users", "developer")
        self.store = {}

    @sync('get_item')
    def get_item(self, *args, **kwargs):
        pass

Manager = User_Manager()