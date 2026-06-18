import pygame

from entities.static_objects import StaticObject
from components.sprite import Sprite
from components.collider import Collider
from core.collision_layers import LAYER_WORLD, MASK_WORLD


class Trader(StaticObject):
    # Edite aqui para alterar o que o trader compra e vende e seus precos
    # Regra de equilibrio: preco da semente < preco do fruto que ela produz
    SHOP_CATALOG: list[dict] = [
        # Sementes a venda (jogador compra do trader)
        {'name': 'corn',   'item_type': 'seed', 'action': 'buy',  'price': 15},
        {'name': 'tomato', 'item_type': 'seed', 'action': 'buy',  'price': 20},
        # Frutos que o trader compra (jogador vende ao trader)
        {'name': 'corn',   'item_type': 'fruit', 'action': 'sell', 'price': 25},
        {'name': 'tomato', 'item_type': 'fruit', 'action': 'sell', 'price': 35},
    ]

    WIDTH: int = 56
    HEIGHT: int = 68

    def __init__(self, position: pygame.Vector2) -> None:
        surface: pygame.Surface = pygame.image.load(
            'assets/images/objects/merchant.png'
        ).convert_alpha()
        surface = pygame.transform.scale(surface, (self.WIDTH, self.HEIGHT))

        super().__init__(
            name='trader',
            position=pygame.Vector2(position),
            size=pygame.Vector2(self.WIDTH, self.HEIGHT),
        )

        self.add_component('sprite', Sprite(self, surface))
        self.add_component('collider', Collider(
            self,
            offset=pygame.Vector2(0, 0),
            size=pygame.Vector2(self.WIDTH, self.HEIGHT),
            layer=LAYER_WORLD,
            mask=MASK_WORLD,
        ))
