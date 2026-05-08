import pygame

from components.sprite import Sprite
from components.collider import Collider

from entities.entity import Entity
from entities.static_objects import StaticObject

from pytmx.util_pygame import load_pygame

class World(Entity):
    def __init__(
        self,
        map_path: str = 'assets/map/map.tmx',
        layers_name: list[str] = ['Water', 'Ground', 'Forest Grass', 'Outside Decoration', 'Hills', 'Fence', 'HouseFloor', 'HouseWalls', 'HouseFurnitureBottom', 'HouseFurnitureTop'],
        music_path: str = 'assets/sounds/music/music.mp3',
    ):
        tmx_data = load_pygame(map_path)
        map_width: int = tmx_data.width * tmx_data.tilewidth
        map_height: int = tmx_data.height * tmx_data.tileheight
        super().__init__('world', (0, 0), size=(map_width, map_height))

        self.tile_width: int = tmx_data.tilewidth
        self.tile_height: int = tmx_data.tileheight
        self.farmable_tiles: set[tuple[int, int]] = set()
        surface: pygame.Surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)
        self.surface: pygame.Surface = surface
        soil_surface = pygame.image.load('assets/images/soil/x.png').convert_alpha()
        if soil_surface.get_size() != (self.tile_width, self.tile_height):
            soil_surface = pygame.transform.scale(soil_surface, (self.tile_width, self.tile_height))
        self.soil_surface: pygame.Surface = soil_surface

        for layer in layers_name:
            layer_data = tmx_data.get_layer_by_name(layer)
            for x, y, tile_image in layer_data.tiles():
                pixel_x = x * tmx_data.tilewidth
                pixel_y = y * tmx_data.tileheight
                surface.blit(tile_image, (pixel_x, pixel_y))

        sprite = Sprite(self, surface)
        self.add_component('sprite', sprite)

        self.music_path: str = music_path
        self._music_started: bool = False

        # Salva posição spwan do player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.spawn = (obj.x, obj.y)

        # Colisao mapeada pela Layer Collision
        collision_layer = tmx_data.get_layer_by_name('Collision')
        for index, (x, y, _tile_image) in enumerate(collision_layer.tiles()):
            collider = Collider(
                self,
                offset=(x * tmx_data.tilewidth, y * tmx_data.tileheight),
                size=(tmx_data.tilewidth, tmx_data.tileheight)
            )
            self.add_component(f'collider_{index}', collider)

        # Area plantavel mapeada pela Layer Farmable
        farmable_layer = tmx_data.get_layer_by_name('Farmable')
        for index, (x, y, _tile_image) in enumerate(farmable_layer.tiles()):
            self.farmable_tiles.add((x, y))

    def is_farmable_tile(self, tile_x: int, tile_y: int) -> bool:
        return (tile_x, tile_y) in self.farmable_tiles

    def till_soil(self, tile_x: int, tile_y: int) -> bool:
        if not self.is_farmable_tile(tile_x, tile_y):
            return False

        pixel_x = tile_x * self.tile_width
        pixel_y = tile_y * self.tile_height
        self.surface.blit(self.soil_surface, (pixel_x, pixel_y))
        return True

    def start_music(self):
        if self._music_started:
            return

        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play(loops=-1)
        self._music_started = True