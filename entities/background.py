import pygame

from entities.entity import Entity
from components.sprite import Sprite


class Background(Entity):
    def __init__(self, path: str = 'assets/images/world/ground.png'):
        surface: pygame.Surface = pygame.image.load(path).convert()
        width, height = surface.get_size()

        super().__init__('background', (0, 0), size=(width, height))

        sprite = Sprite(self, path)
        sprite.set_surface(surface)
        self.add_component('sprite', sprite)
