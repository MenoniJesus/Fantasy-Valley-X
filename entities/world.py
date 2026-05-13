import pygame

from components.component import Component
from components.sprite import Sprite
from components.collider import Collider

from entities.entity import Entity

from pytmx.util_pygame import load_pygame

class World(Entity):
    def __init__(self):        
        tmx_data = load_pygame('assets/map/map.tmx')
        
        self.layers_name: list[str] = [
            'Water', 
            'Ground', 
            'Forest Grass', 
            'Outside Decoration', 
            'Hills', 
            'Fence', 
            'HouseFloor', 
            'HouseWalls', 
            'HouseFurnitureBottom', 
            'HouseFurnitureTop'
        ]
        
        map_width: float = tmx_data.width * tmx_data.tilewidth
        map_height: float = tmx_data.height * tmx_data.tileheight
        
        self.tile_width: int = tmx_data.tilewidth
        self.tile_height: int = tmx_data.tileheight
        
        super().__init__('world', (0, 0), size=(map_width, map_height))
        
        # Cria uma superfície para o mundo e desenha as camadas do mapa nela 
        self.surface: pygame.Surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

        for layer in self.layers_name:
            layer_data = tmx_data.get_layer_by_name(layer)
            for x, y, tile_image in layer_data.tiles():
                pixel_x = x * tmx_data.tilewidth
                pixel_y = y * tmx_data.tileheight
                self.surface.blit(tile_image, (pixel_x, pixel_y))

        sprite = Sprite(self, self.surface)
        self.add_component('sprite', sprite)

        # Salva posição spwan do player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.spawn = (obj.x, obj.y)

        self.load_components_world(tmx_data)
            
        # Música de fundo
        self.music_path: str = 'assets/sounds/music/music.mp3'
        self._music_started: bool = False

    def load_components_world(self, tmx_data):
        self.matrix_components = []
        
        for x_axis in range(tmx_data.height):
            row = []
            for y_axis in range(tmx_data.width):
                component = Component(self)
                row.append(component)
            self.matrix_components.append(row)
        
        # Carrega camada de colisão
        collision_layer = tmx_data.get_layer_by_name('Collision')    
        for x_axis, y_axis, _ in collision_layer.tiles():
            collider = Collider(
                self,
                offset=(x_axis * tmx_data.tilewidth, y_axis * tmx_data.tileheight),
                size=(tmx_data.tilewidth, tmx_data.tileheight)
            )
            self.matrix_components[y_axis][x_axis] = collider
        
        # Carrega camada de farmable
        farmable_layer = tmx_data.get_layer_by_name('Farmable')
        for x_axis, y_axis, _ in farmable_layer.tiles():
            component = self.matrix_components[y_axis][x_axis]
            component.user_data = 'farmable'
        
    def start_music(self):
        if self._music_started:
            return

        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play(loops=-1)
        self._music_started = True