import pygame
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from components.component import Component


TComponent = TypeVar('TComponent')

class Entity:
    def __init__(
        self,
        name: str,
        position: tuple[float, float],
        size: tuple[float, float] = (0, 0),
        speed: float = 0,
        max_health: int = 100,
    ):
        self.name: str = name

        x, y = position
        width, height = size
        self.rect: pygame.FRect = pygame.FRect(float(x), float(y), float(width), float(height))

        self.speed: float = float(speed)
        self.max_health: int = int(max_health)
        self.health: int = int(max_health)

        self.components: dict[str, Any] = {}

    def get_position(self):
        return (self.rect.x, self.rect.y)

    def move(self, delta_x: float, delta_y: float):
        self.rect.x += float(delta_x)
        self.rect.y += float(delta_y)

    def set_speed(self, speed: float):
        self.speed = float(speed)

    def take_damage(self, amount: int):
        self.health = max(0, self.health - int(amount))

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + int(amount))

    def add_component(self, name: str, component: 'Component'):
        self.components[name] = component

    def remove_component(self, name: str):
        if name in self.components:
            del self.components[name]

    def get_component(self, name: str):
        return self.components.get(name)

    def get_components_by_type(self, component_type: type[TComponent]):
        results: list[TComponent] = []

        for component in self.components.values():
            if isinstance(component, component_type):
                results.append(component)

        return results

    def update(self, dt: float):
        pass

    def render(self, dt: float):
        for component in self.components.values():
            if hasattr(component, 'render'):
                component.render(dt)