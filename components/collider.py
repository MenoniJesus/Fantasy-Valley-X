import pygame

from components.component import Component


class Collider(Component):
    def __init__(
        self,
        parent_entity: 'Entity',
        offset: pygame.Vector2 = pygame.Vector2(0, 0),
        size: pygame.Vector2 | None = None,
        layer: int = 1,
        mask: list[int] | None = None,
    ):
        super().__init__(parent_entity)
        self.offset: pygame.Vector2 = pygame.Vector2(offset)
        self.size: pygame.Vector2 | None = pygame.Vector2(size) if size is not None else None
        self.layer: int = layer
        self.mask: list[int] = mask if mask is not None else [1]

    def get_rect(self) -> pygame.FRect:
        if self.size is None:
            width: float = self.parent_entity.rect.width
            height: float = self.parent_entity.rect.height
        else:
            width, height = self.size

        return pygame.FRect(
            self.parent_entity.rect.x + self.offset.x,
            self.parent_entity.rect.y + self.offset.y,
            width,
            height,
        )

    def can_collide_with(self, other: 'Collider') -> bool:
        return self.layer in other.mask or other.layer in self.mask
