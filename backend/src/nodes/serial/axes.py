class axis:
    def __init__(self, _id, name, board, setup, step=1):
        self._id = str(_id)
        self.name = name
        self.position = 'unknow'
        self.trusted = False
        self.acceleration = 0
        self.feedrate = 0
        self.board_id = board

    def set_acceleration(self, acceleration):
        self.acceleration = acceleration
    
    def set_feedrate(self, feedrate):
        self.feedrate = feedrate

    def set_position(self, position):
        self.position = position

    def set_trusted(self, trusted):
        self.trusted = trusted
    
    @property
    def status(self):
        return {
            'name': self.name,
            'position': self.position,
            'trusted': self.trusted,
            'acceleration': self.acceleration,
            'feedrate': self.feedrate
        }
