import pygame

from components.sprite import Sprite
from entities.entity import Entity
from core.settings import TILE_SIZE


class Plant(Entity):
    def __init__(self, name: str, tile_pos: tuple[int, int]):
        tile_x, tile_y = tile_pos

        growth_frames: list[pygame.Surface] = [
            pygame.image.load(f'assets/images/fruit/{name}/{i}.png').convert_alpha()
            for i in range(4)
        ]

        super().__init__(
            name=name,
            position=pygame.Vector2(tile_x * TILE_SIZE, tile_y * TILE_SIZE),
            size=pygame.Vector2(TILE_SIZE, TILE_SIZE),
        )

        self.growth_frames: list[pygame.Surface] = growth_frames
        self.tile_pos: tuple[int, int] = tile_pos
        self.current_day: int = 0
        self.growth_stage: int = 0
        self.is_watered_today: bool = False
        self.is_fully_grown: bool = False

        frame: pygame.Surface = growth_frames[0]
        sprite_w, sprite_h = frame.get_size()
        offset: pygame.Vector2 = pygame.Vector2(
            (TILE_SIZE - sprite_w) / 2,
            (TILE_SIZE - sprite_h) / 2,
        )
        self.add_component('sprite', Sprite(self, frame, offset=offset))

    def advance_day(self) -> None:
        if not self.is_watered_today:
            return

        self.current_day += 1
        self.growth_stage = self.current_day

        frame: pygame.Surface = self.growth_frames[min(self.growth_stage, 3)]
        sprite_w, sprite_h = frame.get_size()
        offset: pygame.Vector2 = pygame.Vector2(
            (TILE_SIZE - sprite_w) / 2,
            (TILE_SIZE - sprite_h) / 2,
        )
        sprite = self.get_component('sprite')
        sprite.set_surface(frame)
        sprite.offset = offset

        if self.current_day >= 3:
            self.is_fully_grown = True

        self.is_watered_today = False
