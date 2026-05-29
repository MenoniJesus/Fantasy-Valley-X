import pygame

from components.sprite import Sprite


class RenderSystem:
    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen

    def render(
        self,
        screen: pygame.Surface,
        sprite: Sprite | pygame.Surface,
        position: pygame.Vector2 | None = None,
        camera_offset: pygame.Vector2 | None = None,
    ) -> None:
        if isinstance(sprite, Sprite):
            surface: pygame.Surface = sprite.get_surface()
            render_pos: pygame.Vector2 = sprite.get_render_position()
        else:
            surface = sprite
            render_pos = position if position is not None else pygame.Vector2(0, 0)

        if camera_offset is not None:
            render_pos = render_pos - camera_offset

        screen.blit(surface, render_pos)
