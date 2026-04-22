import pygame

from components.sprite import Sprite
from entities.entity import Entity


class World(Entity):
    def __init__(
        self,
        background_path: str = 'assets/images/world/ground.png',
        music_path: str = 'assets/sounds/music/music.mp3',
    ):
        surface: pygame.Surface = pygame.image.load(background_path).convert()
        width, height = surface.get_size()

        super().__init__('world', (0, 0), size=(width, height), max_health=1)

        sprite = Sprite(self, background_path)
        sprite.set_surface(surface)
        self.add_component('sprite', sprite)

        self.music_path: str = music_path
        self._music_started: bool = False

    def start_music(self):
        if self._music_started:
            return

        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play(loops=-1)
        self._music_started = True
