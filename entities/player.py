import os

import pygame

from components.animation import Animation
from components.collider import Collider
from components.sound import Sound
from components.sprite import Sprite
from entities.entity import Entity


class Player(Entity):
    def __init__(self, position: tuple[float, float]):
        clips: dict[str, list[pygame.Surface]] = {
            'idle_down': self._load_clip('assets/images/character/down_idle'),
            'idle_up': self._load_clip('assets/images/character/up_idle'),
            'idle_left': self._load_clip('assets/images/character/left_idle'),
            'idle_right': self._load_clip('assets/images/character/right_idle'),
            'walk_down': self._load_clip('assets/images/character/down'),
            'walk_up': self._load_clip('assets/images/character/up'),
            'walk_left': self._load_clip('assets/images/character/left'),
            'walk_right': self._load_clip('assets/images/character/right'),
        }

        initial_surface: pygame.Surface = clips['idle_down'][0]
        width, height = initial_surface.get_size()
        initial_path: str = 'assets/images/character/down_idle/0.png'

        spawn_x, spawn_y = position
        super().__init__(
            name='player',
            position=(spawn_x, spawn_y),
            size=(width, height),
            speed=250,
            max_health=100,
        )

        sprite = Sprite(self, initial_path)
        sprite.set_surface(initial_surface)

        self.add_component('sprite', sprite)
        self.add_component('collider', Collider(self))
        self.add_component('animation', Animation(clips=clips, initial_state='idle_down'))
        self.add_component('axe_sound', Sound('assets/sounds/sfx/axe.mp3'))
        self.add_component('hoe_sound', Sound('assets/sounds/sfx/hoe.wav'))

    def _load_clip(self, folder_path: str):
        frames: list[pygame.Surface] = [
            pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            for filename in sorted(os.listdir(folder_path))
            if filename.endswith('.png')
        ]

        if not frames:
            raise ValueError(f'Nenhum frame encontrado em: {folder_path}')

        return frames
