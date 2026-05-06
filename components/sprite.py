import pygame

from components.component import Component

class Sprite(Component):
    def __init__(self, parent_entity: 'Entity', surface: pygame.Surface):
        super().__init__(parent_entity)
        self.surface = surface

    def get_surface(self):
        return self.surface

    def set_surface(self, surface: pygame.Surface):
        self.surface = surface
