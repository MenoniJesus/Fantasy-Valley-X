import pygame

from entities.entity import Entity
from components.sprite import Sprite
from components.collider import Collider

class StaticObject(Entity):
    def __init__(self, name: str, position: tuple[float, float], surface: 'pygame.Surface'):
        width, height = surface.get_size()
        super().__init__(name=name, position=position, size=(width, height))

        collider = Collider(self, offset=(0, 0), size=(width, height))
        self.add_component('collider', collider)

        sprite = Sprite(self, surface)
        self.add_component('sprite', sprite)