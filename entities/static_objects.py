import pygame

from entities.entity import Entity
from components.sprite import Sprite
from components.collider import Collider


class StaticObject(Entity):
    def __init__(self, name: str, position: pygame.Vector2, surface: pygame.Surface):
        w, h = surface.get_size()
        super().__init__(
            name=name,
            position=pygame.Vector2(position),
            size=pygame.Vector2(w, h),
        )

        collider = Collider(
            self,
            offset=pygame.Vector2(0, 0),
            size=pygame.Vector2(w, h),
        )
        self.add_component('collider', collider)

        sprite = Sprite(self, surface)
        self.add_component('sprite', sprite)
