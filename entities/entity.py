import pygame
from typing import Any, TypeVar

TComponent = TypeVar('TComponent')


class Entity:
    def __init__(
        self,
        name: str,
        position: pygame.Vector2,
        size: pygame.Vector2 = pygame.Vector2(0, 0),
    ):
        self.name: str = name

        pos: pygame.Vector2 = pygame.Vector2(position)
        sz: pygame.Vector2 = pygame.Vector2(size)
        self.rect: pygame.FRect = pygame.FRect(
            float(pos.x), float(pos.y),
            float(sz.x),  float(sz.y),
        )

        self.components: dict[str, Any] = {}

    def get_position(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.x, self.rect.y)

    def get_size(self) -> pygame.Vector2:
        return pygame.Vector2(self.rect.width, self.rect.height)

    def move(self, delta_x: float, delta_y: float) -> None:
        self.rect.x += float(delta_x)
        self.rect.y += float(delta_y)

    def add_component(self, name: str, component: 'Component') -> None:
        self.components[name] = component

    def remove_component(self, name: str) -> None:
        if name in self.components:
            del self.components[name]

    def get_component(self, name: str) -> Any:
        return self.components.get(name)

    def get_components_by_type(self, component_type: type[TComponent]) -> list[TComponent]:
        results: list[TComponent] = []
        for component in self.components.values():
            if isinstance(component, component_type):
                results.append(component)
        return results

    def update(self, dt: float) -> None:
        pass

    def render(self, dt: float) -> None:
        for component in self.components.values():
            if hasattr(component, 'render'):
                component.render(dt)
