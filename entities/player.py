import os

import pygame

from components.animation import Animation
from components.hitbox import Hitbox
from components.sound import Sound
from components.sprite import Sprite
from components.velocity import Velocity
from entities.entity import Entity


class Player(Entity):
    def __init__(self, position):
        clips = {
            'idle_down': self._load_clip('assets/images/character/down_idle'),
            'idle_up': self._load_clip('assets/images/character/up_idle'),
            'idle_left': self._load_clip('assets/images/character/left_idle'),
            'idle_right': self._load_clip('assets/images/character/right_idle'),
            'walk_down': self._load_clip('assets/images/character/down'),
            'walk_up': self._load_clip('assets/images/character/up'),
            'walk_left': self._load_clip('assets/images/character/left'),
            'walk_right': self._load_clip('assets/images/character/right'),
        }

        initial_surface = clips['idle_down'][0]
        width, height = initial_surface.get_size()
        initial_path = 'assets/images/character/down_idle/0.png'

        components = {
            'sprite': Sprite(width, height, initial_path),
            'hitbox_collision': Hitbox(pygame.Rect(position.x, position.y, width, height)),
            'velocity': Velocity(250),
            'animation': Animation(clips=clips, initial_state='idle_down'),
            'axe_sound': Sound('assets/sounds/sfx/axe.mp3'),
            'hoe_sound': Sound('assets/sounds/sfx/hoe.wav'),
        }

        super().__init__(position, components)
        self.components['sprite'].set_surface(initial_surface)

    def _load_clip(self, folder_path):
        return [
            pygame.image.load(os.path.join(folder_path, filename))
            for filename in os.listdir(folder_path)
            if filename.endswith('.png')
        ]
        