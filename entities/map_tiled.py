import pygame
from pytmx.util_pygame import load_pygame

from components.layer import Layer
from entities.entity import Entity


class MapTiled(Entity):
    def __init__(self, tmx_path, layer_order, object_group_order):
        self.tmx_data = load_pygame(tmx_path)

        world_width = self.tmx_data.width * self.tmx_data.tilewidth
        world_height = self.tmx_data.height * self.tmx_data.tileheight

        components = {
            'layers': {},
            'objects': {},
            'collision': [],
            'farmable': [],
        }

        super().__init__(pygame.Vector2(0, 0), components)

        self.world_width = world_width
        self.world_height = world_height
        self.layer_order = layer_order
        self.object_group_order = object_group_order

        self._build_tile_layers()
        self._build_object_groups()
        self._build_logic_layers()

    def _build_tile_layers(self):
        for draw_order, layer_name in enumerate(self.layer_order):
            layer = self.tmx_data.get_layer_by_name(layer_name)
            surface = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)

            for x, y, tile_surface in layer.tiles():
                surface.blit(
                    tile_surface,
                    (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight),
                )

            self.components['layers'][layer_name] = Layer(
                name=layer_name,
                surface=surface,
                position=(0, 0),
                draw_order=draw_order,
                kind='tile',
            )

    def _build_object_groups(self):
        for group_name in self.object_group_order:
            group = self.tmx_data.get_layer_by_name(group_name)
            objects = []

            for obj in group:
                objects.append({
                    'name': obj.name,
                    'x': obj.x,
                    'y': obj.y,
                    'width': obj.width,
                    'height': obj.height,
                    'gid': getattr(obj, 'gid', None),
                    'image': getattr(obj, 'image', None),
                })

            self.components['objects'][group_name] = objects

    def _build_logic_layers(self):
        self.components['collision'] = self._extract_tile_rects('Collision')
        self.components['farmable'] = self._extract_tile_rects('Farmable')

    def _extract_tile_rects(self, layer_name):
        layer = self.tmx_data.get_layer_by_name(layer_name)
        rects = []

        for x, y, _ in layer.tiles():
            rects.append(
                pygame.Rect(
                    x * self.tmx_data.tilewidth,
                    y * self.tmx_data.tileheight,
                    self.tmx_data.tilewidth,
                    self.tmx_data.tileheight,
                )
            )

        return rects

    def get_render_layers(self, layer_names):
        return [self.components['layers'][name] for name in layer_names]

    def get_object_group(self, group_name):
        return self.components['objects'].get(group_name, [])

    def get_player_start(self):
        for obj in self.get_object_group('Player'):
            if obj.get('name') == 'Start':
                return (obj['x'], obj['y'])

        return None
