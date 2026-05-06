class Component:
    def __init__(self, parent_entity: 'Entity'):
        self.parent_entity: 'Entity' = parent_entity

    def update(self, dt: float):
        pass

    def render(self, dt: float):
        pass