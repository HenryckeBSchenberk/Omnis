from bson import ObjectId as new_id
class axis:
    def __init__(self, _id, name, board, sensors):
        self._id = new_id(_id)
        self.name = name
        self.board_id = board
        self.sensors = sensors
        self.position = 'unknow'

    def set_position(self, position):
        self.position = position
    
    @property
    def trusted(self):
        return all([sn.trusted for sn in self.sensors]) and self.position != 'unknow'

    @property
    def status(self):
        return {
            'name': self.name,
            'position': self.position,
            'trusted': self.trusted
        }
