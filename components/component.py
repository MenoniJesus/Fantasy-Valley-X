class Component:
    def __init__(self, parent_entity: 'Entity', user_data: str = None):
        self.parent_entity: 'Entity' = parent_entity
        self.user_data: str = user_data

    def update(self, dt: float):
        pass

    def render(self, dt: float):
        pass