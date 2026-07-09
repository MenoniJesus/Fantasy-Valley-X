import os

import pygame

from components.animation import Animation
from components.collider import Collider
from components.sound import Sound
from components.sprite import Sprite

from entities.dynamic_object import DynamicObject

from core.collision_layers import LAYER_PLAYER, LAYER_TOOL, MASK_PLAYER, MASK_TOOL
from core.inventory import Inventory
from core.settings import TILE_SIZE


class Player(DynamicObject):
    def __init__(self, position: pygame.Vector2):
        clips: dict[str, list[pygame.Surface]] = {
            # Movimentacao
            'idle_down': self._load_clip('assets/images/character/down_idle'),
            'idle_up': self._load_clip('assets/images/character/up_idle'),
            'idle_left': self._load_clip('assets/images/character/left_idle'),
            'idle_right': self._load_clip('assets/images/character/right_idle'),

            'walk_down': self._load_clip('assets/images/character/down'),
            'walk_up': self._load_clip('assets/images/character/up'),
            'walk_left': self._load_clip('assets/images/character/left'),
            'walk_right': self._load_clip('assets/images/character/right'),

            # Uso de ferramentas
            'down_hoe': self._load_clip('assets/images/character/down_hoe'),
            'up_hoe': self._load_clip('assets/images/character/up_hoe'),
            'left_hoe': self._load_clip('assets/images/character/left_hoe'),
            'right_hoe': self._load_clip('assets/images/character/right_hoe'),

            'down_axe': self._load_clip('assets/images/character/down_axe'),
            'up_axe': self._load_clip('assets/images/character/up_axe'),
            'left_axe': self._load_clip('assets/images/character/left_axe'),
            'right_axe': self._load_clip('assets/images/character/right_axe'),

            'down_water': self._load_clip('assets/images/character/down_water'),
            'up_water': self._load_clip('assets/images/character/up_water'),
            'left_water': self._load_clip('assets/images/character/left_water'),
            'right_water': self._load_clip('assets/images/character/right_water'),
        }

        initial_surface: pygame.Surface = clips['idle_down'][0]
        w, h = initial_surface.get_size()

        super().__init__(
            name='player',
            position=pygame.Vector2(position),
            size=pygame.Vector2(w, h),
            speed=250
        )

        self.tool_active: bool = False
        self.current_direction: str = 'down'
        self.inventory: Inventory = Inventory.create_default()
        self.nonicoins: int = 100

        self.add_component('sprite', Sprite(self, initial_surface))

        self.add_component('collider', Collider(
            self,
            offset=pygame.Vector2(64, 48),
            size=pygame.Vector2(44, 48),
            layer=LAYER_PLAYER,
            mask=MASK_PLAYER,
        ))

        self.add_component('tool_collider', Collider(
            self,
            offset=pygame.Vector2(0, 0),
            size=pygame.Vector2(TILE_SIZE, TILE_SIZE),
            layer=LAYER_TOOL,
            mask=MASK_TOOL,
        ))

        self.add_component('animation', Animation(clips=clips, initial_state='idle_down'))
        self.add_component('axe_sound', Sound('assets/sounds/sfx/axe.mp3'))
        self.add_component('hoe_sound', Sound('assets/sounds/sfx/hoe.wav'))
        self.add_component('water_sound', Sound('assets/sounds/sfx/water.mp3'))

    def _load_clip(self, folder_path: str) -> list[pygame.Surface]:
        frames: list[pygame.Surface] = [
            pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            for filename in sorted(os.listdir(folder_path))
            if filename.endswith('.png')
        ]
        return frames

    def update_tool_collider(self) -> None:
        center: pygame.Vector2 = pygame.Vector2(
            self.get_component('collider').get_rect().center
        )

        tile_x: int = int(center.x // TILE_SIZE)
        tile_y: int = int(center.y // TILE_SIZE)

        direction: str = self.current_direction
        if direction == 'right':
            delta: pygame.Vector2 = pygame.Vector2(1, 0)
        elif direction == 'left':
            delta = pygame.Vector2(-1, 0)
        elif direction == 'down':
            delta = pygame.Vector2(0, 1)
        else:  # up
            delta = pygame.Vector2(0, -1)
        target: pygame.Vector2 = (pygame.Vector2(tile_x, tile_y) + delta) * TILE_SIZE

        tool_collider: Collider = self.get_component('tool_collider')
        tool_collider.offset = target - pygame.Vector2(self.rect.topleft)
        tool_collider.size = pygame.Vector2(TILE_SIZE, TILE_SIZE)

    def activate_tool(self, direction: str) -> None:
        self.current_direction = direction
        self.tool_active = True
        self.update_tool_collider()

    def deactivate_tool(self) -> None:
        self.tool_active = False

    def hoe_tile(self, tile_x: int, tile_y: int) -> None:
        print(f'Arando tile ({tile_x}, {tile_y})')
