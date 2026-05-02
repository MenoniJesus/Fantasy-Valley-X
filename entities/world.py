import pygame

from components.sprite import Sprite
from entities.entity import Entity
from pytmx.util_pygame import load_pygame

class World(Entity):
    def __init__(
        self,
        map_path: str = 'assets/map/map.tmx',
        layers_name: list[str] = ['Ground', 'Water', 'Forest Grass', 'Hills', 'Fence', 'HouseFloor', 'HouseWalls', 'HouseFurnitureBottom', 'HouseFurnitureTop', 'Outside Decoration'],
        music_path: str = 'assets/sounds/music/music.mp3',
    ):
        tmx_data = load_pygame(map_path)

        map_width: int = tmx_data.width * tmx_data.tilewidth
        map_height: int = tmx_data.height * tmx_data.tileheight

        surface: pygame.Surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

        for layer in layers_name:
            layer_data = tmx_data.get_layer_by_name(layer)
            for x, y, tile_image in layer_data.tiles():
                pixel_x = x * tmx_data.tilewidth
                pixel_y = y * tmx_data.tileheight
                surface.blit(tile_image, (pixel_x, pixel_y))

        super().__init__('world', (0, 0), size=(map_width, map_height))

        sprite = Sprite(self, surface)
        self.add_component('sprite', sprite)

        self.music_path: str = music_path
        self._music_started: bool = False

    def start_music(self):
        if self._music_started:
            return

        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play(loops=-1)
        self._music_started = True