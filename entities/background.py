import pygame

from entities.entity import Entity
from components.sprite import Sprite


class Background(Entity):
    def __init__(self, path='assets/images/world/ground.png'):
        surface = pygame.image.load(path)
        width, height = surface.get_size()

        super().__init__(pygame.Vector2(0, 0), components={
            'sprite': Sprite(width, height, path),
        })
