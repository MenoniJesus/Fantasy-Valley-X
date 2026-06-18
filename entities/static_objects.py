import pygame

from entities.entity import Entity
from components.sprite import Sprite


class StaticObject(Entity):
    def __init__(
        self,
        name: str,
        position: pygame.Vector2,
        size: pygame.Vector2 | None = None,
        surface: pygame.Surface | None = None,
    ):
        if size is None:
            size = pygame.Vector2(surface.get_size()) if surface is not None else pygame.Vector2(0, 0)
        super().__init__(name=name, position=position, size=size)
        if surface is not None:
            self.add_component('sprite', Sprite(self, surface))
