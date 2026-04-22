import pygame
from typing import TYPE_CHECKING

from components.component import Component

if TYPE_CHECKING:
    from entities.entity import Entity


class Sprite(Component):
    def __init__(self, parent_entity: 'Entity', path: str):
        super().__init__(parent_entity)
        self.path: str = path
        self.surface: pygame.Surface = pygame.image.load(path).convert_alpha()

    def get_path(self):
        return self.path

    def get_size(self):
        return self.surface.get_size()

    def get_surface(self):
        return self.surface

    def set_surface(self, surface: pygame.Surface):
        self.surface = surface
