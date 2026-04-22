import pygame
from typing import TYPE_CHECKING

from components.component import Component

if TYPE_CHECKING:
    from entities.entity import Entity


class Collider(Component):
    def __init__(
        self,
        parent_entity: 'Entity',
        offset: tuple[float, float] = (0, 0),
        size: tuple[float, float] | None = None,
    ):
        super().__init__(parent_entity)
        self.offset: tuple[float, float] = offset
        self.size: tuple[float, float] | None = size

    def get_rect(self):
        if self.size is None:
            width: float = self.parent_entity.rect.width
            height: float = self.parent_entity.rect.height
        else:
            width, height = self.size

        return pygame.FRect(
            self.parent_entity.rect.x + self.offset[0],
            self.parent_entity.rect.y + self.offset[1],
            width,
            height,
        )