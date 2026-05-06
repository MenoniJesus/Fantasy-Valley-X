import pygame

from components.sprite import Sprite

class RenderSystem:
    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen

    def render(
        self,
        sprite: Sprite | pygame.Surface,
        position: tuple[float, float] = (0, 0),
        camera: 'CameraSystem | None' = None,
    ):
        if isinstance(sprite, Sprite):
            surface: pygame.Surface = sprite.get_surface()
        else:
            surface = sprite

        if camera is not None:
            position = camera.to_screen(position)
                    
        self.screen.blit(surface, position)