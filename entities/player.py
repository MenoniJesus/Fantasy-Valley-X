import os

import pygame

from components.animation import Animation
from components.collider import Collider
from components.sound import Sound
from components.sprite import Sprite

from entities.entity import Entity

from entities.world import World

class Player(Entity):
    def __init__(self, position: tuple[float, float]):
        clips: dict[str, list[pygame.Surface]] = {
            # Movimentação
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
        width, height = initial_surface.get_size()

        spawn_x, spawn_y = position
        super().__init__(
            name='player',
            position=(spawn_x, spawn_y),
            size=(width, height),
            speed=250
        )

        self.tool_in_use: int = 0  # 0: Hoe, 1: Axe, 2: Watering Can

        sprite = Sprite(self, initial_surface)

        self.add_component('sprite', sprite)
        self.add_component('collider', Collider(self, offset=(64, 48), size=(44, 48)))
        self.add_component('animation', Animation(clips=clips, initial_state='idle_down'))
        self.add_component('axe_sound', Sound('assets/sounds/sfx/axe.mp3'))
        self.add_component('hoe_sound', Sound('assets/sounds/sfx/hoe.wav'))

    def _load_clip(self, folder_path: str):
        frames: list[pygame.Surface] = [
            pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            for filename in sorted(os.listdir(folder_path))
            if filename.endswith('.png')
        ]

        return frames

    def cut_grass(self, world: World, direction: str):
        target_tile = self._get_tool_target_tile(world, direction)
        if target_tile is None:
            return

        tile_x, tile_y = target_tile
        if world.till_soil(tile_x, tile_y):
            print('Bora arar a terra')

    def _get_tool_target_tile(self, world: World, direction: str) -> tuple[int, int] | None:
        tile_w = world.tile_width
        tile_h = world.tile_height
        center_x, center_y = self.rect.center

        if direction == 'up':
            target_x, target_y = center_x, center_y - tile_h
        elif direction == 'down':
            target_x, target_y = center_x, center_y + tile_h
        elif direction == 'left':
            target_x, target_y = center_x - tile_w, center_y
        elif direction == 'right':
            target_x, target_y = center_x + tile_w, center_y
        else:
            return None

        if not (0 <= target_x < world.rect.width and 0 <= target_y < world.rect.height):
            return None

        tile_x = int(target_x // tile_w)
        tile_y = int(target_y // tile_h)
        return (tile_x, tile_y)