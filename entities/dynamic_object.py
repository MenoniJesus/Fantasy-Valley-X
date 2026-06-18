import pygame

from entities.entity import Entity


class DynamicObject(Entity):
    def __init__(
        self,
        name: str,
        position: pygame.Vector2,
        size: pygame.Vector2 = pygame.Vector2(0, 0),
        speed: float = 0,
    ):
        super().__init__(name=name, position=position, size=size)
        self.speed: float = float(speed)

    def set_speed(self, speed: float) -> None:
        self.speed = float(speed)
