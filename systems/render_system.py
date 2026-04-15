import pygame

from components.sprite import Sprite

class RenderSystem:
    def __init__(self, screen):
        self.screen = screen

    def render(self, sprite, position=(0, 0), camera=None):
        if isinstance(sprite, Sprite):
            surface = sprite.get_surface()
        else:
            surface = sprite

        if camera is not None:
            position = camera.to_screen(position)
                    
        self.screen.blit(surface, position)