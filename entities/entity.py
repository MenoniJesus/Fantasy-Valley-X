class Entity:
    def __init__(self, position, components):
        self.position_X = position.x
        self.position_Y = position.y
        self.components = components

    def get_position(self):
        return (self.position_X, self.position_Y)