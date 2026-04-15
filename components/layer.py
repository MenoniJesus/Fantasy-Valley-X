class Layer:
    def __init__(self, name, surface, position=(0, 0), draw_order=0, kind='tile'):
        self.name = name
        self.surface = surface
        self.position = position
        self.draw_order = draw_order
        self.kind = kind
