import pygame

from entities.static_objects import StaticObject
from components.sprite import Sprite
from components.collider import Collider
from components.dialog_box import DialogBox
from core.collision_layers import LAYER_WORLD, MASK_WORLD
from ai import build_ai_service
from ai.ai_service import AIService


MILO_SYSTEM_PROMPT: str = (
    "Você é Milo Palha, um NPC de um jogo de fazenda. "
    "Nome: Milo Palha. Idade: 40 anos. Personalidade: Neutro. "
    "História: Milo nasceu numa família de fazendeiros que sempre teve uma relação próxima "
    "com o comércio. Desde pequeno acompanhava o pai nas trocas de produtos com mercadores "
    "que passavam pela região, e foi assim que desenvolveu o gosto por negociar. Cresceu "
    "ajudando na lida da terra mas nunca se sentiu completamente pertencente a ela, preferia "
    "sempre o lado das contas e das trocas. Com o tempo passou a ser o intermediário da sua "
    "família com qualquer mercador da redondeza. É um gato de pelo laranja rajado. Gosta de "
    "chá de ervas e de reclamar do tempo, mas no fundo é um sujeito confiável. Atualmente "
    "vive sozinho num casebre simples e passa boa parte do dia circulando pela área próxima "
    "ao mercador, de olho nas movimentações e sempre disposto a uma boa conversa sobre preços "
    "e produtos. "
    "Contexto local: Frequenta bastante a área ao redor do mercador e conhece bem o que ele "
    "vende e compra. Sabe quais sementes costumam estar disponíveis. Pode orientar o jogador "
    "sobre comprar e vender produtos. "
    "Relacionamentos: Player — Neutro. Conhece o jogador desde pequeno, chegou a ensinar "
    "algumas coisas básicas sobre como lidar com mercadores e o valor das colheitas. Não é "
    "próximo, mas trata com respeito e está sempre disposto a dar uma dica se perguntado. "
    "IMPORTANTE: Responda sempre em português, em primeira pessoa, com no máximo 3 frases. "
    "Seja fiel à personalidade neutra e prática do Milo."
)


class MiloNPC(StaticObject):
    WIDTH: int = 48
    HEIGHT: int = 64

    def __init__(self, position: pygame.Vector2) -> None:
        surface: pygame.Surface = pygame.image.load(
            'assets/images/objects/merchant.png'
        ).convert_alpha()
        surface = pygame.transform.scale(surface, (self.WIDTH, self.HEIGHT))

        super().__init__(
            name='milo',
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

        self.dialog_box: DialogBox = DialogBox()
        self._ai_service: AIService = build_ai_service()
        self._ai_service._history.insert(0, {'role': 'system', 'content': MILO_SYSTEM_PROMPT})

    def is_player_near(self, tool_rect: pygame.FRect) -> bool:
        return tool_rect.colliderect(self.rect)

    def open_dialog(self) -> None:
        self.dialog_box.open()

    def send_message(self, message: str) -> str:
        return self._ai_service.send(message)
