import pygame

from components.component import Component
from components.sprite import Sprite
from components.collider import Collider

from entities.entity import Entity

from core.collision_layers import LAYER_WORLD, LAYER_FARMABLE, MASK_WORLD, MASK_FARMABLE
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

        super().__init__(
            'world',
            pygame.Vector2(0, 0),
            size=pygame.Vector2(map_width, map_height),
        )

        # Cria uma superficie para o mundo e desenha as camadas do mapa nela
        self.surface: pygame.Surface = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

        for layer in self.layers_name:
            layer_data = tmx_data.get_layer_by_name(layer)
            for x, y, tile_image in layer_data.tiles():
                pixel_x: int = x * tmx_data.tilewidth
                pixel_y: int = y * tmx_data.tileheight
                self.surface.blit(tile_image, (pixel_x, pixel_y))

        sprite: Sprite = Sprite(self, self.surface)
        self.add_component('sprite', sprite)

        # Salva posicao de spawn do player, posicao da cama e do trader como Vector2
        self.spawn: pygame.Vector2 = pygame.Vector2(0, 0)
        self.bed_position: pygame.Vector2 = pygame.Vector2(0, 0)
        self.trader_position: pygame.Vector2 = pygame.Vector2(0, 0)
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.spawn = pygame.Vector2(obj.x, obj.y)
            if obj.name == 'Bed':
                self.bed_position = pygame.Vector2(obj.x, obj.y)
            if obj.name == 'Trader':
                self.trader_position = pygame.Vector2(obj.x, obj.y)

        self.load_components_world(tmx_data)

        # Musica de fundo
        self.music_path: str = 'assets/sounds/music/music.mp3'
        self._music_started: bool = False

    def load_components_world(self, tmx_data) -> None:
        self.matrix_components: list[list[Component]] = []

        for x_axis in range(tmx_data.height):
            row: list[Component] = []
            for y_axis in range(tmx_data.width):
                component: Component = Component(self)
                row.append(component)
            self.matrix_components.append(row)

        # Carrega camada de colisao: um Collider por tile de obstrucao
        collision_layer = tmx_data.get_layer_by_name('Collision')
        for x_axis, y_axis, _ in collision_layer.tiles():
            collider: Collider = Collider(
                self,
                offset=pygame.Vector2(x_axis * tmx_data.tilewidth, y_axis * tmx_data.tileheight),
                size=pygame.Vector2(tmx_data.tilewidth, tmx_data.tileheight),
                layer=LAYER_WORLD,
                mask=MASK_WORLD,
            )
            self.add_component(f'collider_{x_axis}_{y_axis}', collider)

        # Carrega camada farmable
        farmable_layer = tmx_data.get_layer_by_name('Farmable')
        for x_axis, y_axis, _ in farmable_layer.tiles():
            self.matrix_components[y_axis][x_axis].user_data = 'farmable'

            farmable_collider: Collider = Collider(
                self,
                offset=pygame.Vector2(x_axis * tmx_data.tilewidth, y_axis * tmx_data.tileheight),
                size=pygame.Vector2(tmx_data.tilewidth, tmx_data.tileheight),
                layer=LAYER_FARMABLE,
                mask=MASK_FARMABLE,
            )
            self.add_component(f'farmable_{x_axis}_{y_axis}', farmable_collider)

    def start_music(self) -> None:
        if self._music_started:
            return

        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play(loops=-1)
        self._music_started = True
