import pygame

from components.component import Component


class Sprite(Component):
    def __init__(
        self,
        parent_entity: 'Entity',
        surface: pygame.Surface,
        offset: pygame.Vector2 = pygame.Vector2(0, 0),
        size: pygame.Vector2 | None = None,
    ):
        super().__init__(parent_entity)
        self.surface: pygame.Surface = surface
        self.offset: pygame.Vector2 = pygame.Vector2(offset)
        self.size: pygame.Vector2 | None = pygame.Vector2(size) if size is not None else None

    def get_surface(self) -> pygame.Surface:
        if self.size is not None:
            return pygame.transform.scale(self.surface, (int(self.size.x), int(self.size.y)))
        return self.surface

    def set_surface(self, surface: pygame.Surface) -> None:
        self.surface = surface

    def get_render_position(self) -> pygame.Vector2:
        return pygame.Vector2(self.parent_entity.rect.topleft) + self.offset
