import pygame

from components.collider import Collider
from entities.entity import Entity


def get_mtv(rect_a: pygame.FRect, rect_b: pygame.FRect) -> pygame.Vector2 | None:
    intersection: pygame.FRect = rect_a.clip(rect_b)

    if intersection.width == 0 or intersection.height == 0:
        return None

    overlap_x: float = intersection.width
    overlap_y: float = intersection.height

    center_a: pygame.Vector2 = pygame.Vector2(rect_a.centerx, rect_a.centery)
    center_b: pygame.Vector2 = pygame.Vector2(rect_b.centerx, rect_b.centery)

    if overlap_x < overlap_y:
        # Menor no eixo X
        sign_x: float = -1.0 if center_a.x < center_b.x else 1.0
        return pygame.Vector2(sign_x * overlap_x, 0.0)
    else:
        # Menor no eixo Y
        sign_y: float = -1.0 if center_a.y < center_b.y else 1.0
        return pygame.Vector2(0.0, sign_y * overlap_y)


class CollisionSystem:
    def __init__(self) -> None:
        pass

    def get_colliders(self, entity: Entity) -> list[Collider]:
        return entity.get_components_by_type(Collider)
