import pygame

from components.sprite import Sprite

class RenderSystem:
    def __init__(self, screen):
        self.screen = screen

    def render(self, entity):
        for component in entity.components:
            if isinstance(component, Sprite):
                pygame.draw.circle(
                    self.screen,
                    "red",
                    (entity.position_X, entity.position_Y),
                    component.width
                )