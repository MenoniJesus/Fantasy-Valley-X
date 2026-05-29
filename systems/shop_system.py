from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from core.inventory import Item, _load_icon
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from entities.player import Player


class ShopSystem:
    PANEL_WIDTH: int = 440
    PANEL_HEIGHT: int = 420
    BG_COLOR: tuple[int, int, int, int] = (0, 0, 0, 160)
    PANEL_COLOR: tuple[int, int, int] = (40, 30, 20)
    PANEL_BORDER: tuple[int, int, int] = (180, 140, 60)
    TEXT_COLOR: tuple[int, int, int] = (255, 245, 200)
    SELECTED_COLOR: tuple[int, int, int] = (80, 60, 20)
    PRICE_COLOR_BUY: tuple[int, int, int] = (255, 100, 80)
    PRICE_COLOR_SELL: tuple[int, int, int] = (80, 220, 80)
    FEEDBACK_FRAMES: int = 120

    def __init__(self) -> None:
        self.is_open: bool = False
        self.selected_index: int = 0
        self.catalog: list[dict] = []

        self._feedback: str = ''
        self._feedback_timer: int = 0

        self._font_title: pygame.font.Font = pygame.font.SysFont(None, 42)
        self._font_item: pygame.font.Font = pygame.font.SysFont(None, 30)
        self._font_price: pygame.font.Font = pygame.font.SysFont(None, 26)
        self._font_feedback: pygame.font.Font = pygame.font.SysFont(None, 32)
        self._font_hint: pygame.font.Font = pygame.font.SysFont(None, 24)

    def open(self, catalog: list[dict]) -> None:
        """Abre a janela da loja com o catalogo do trader."""
        self.is_open = True
        self.catalog = catalog
        self.selected_index = 0

    def close(self) -> None:
        """Fecha a janela da loja."""
        self.is_open = False

    def navigate(self, direction: int) -> None:
        """Navega entre os itens (-1 = cima, +1 = baixo)."""
        if not self.catalog:
            return
        self.selected_index = (self.selected_index + direction) % len(self.catalog)

    def confirm(self, player: Player) -> str | None:
        """
        Confirma a acao do item selecionado.
        Retorna mensagem de feedback ou None.
        """
        if not self.catalog:
            return None

        entry: dict = self.catalog[self.selected_index]

        if entry['action'] == 'buy':
            if player.nonicoins < entry['price']:
                msg = 'Sem Nonicoins!'
            else:
                icon: pygame.Surface = _load_icon(
                    f'assets/images/overlay/{entry["name"]}.png'
                )
                item: Item = Item(entry['name'], entry['item_type'], 1, icon)
                adicionado: bool = player.inventory.add_item(item)
                if adicionado:
                    player.nonicoins -= entry['price']
                    msg = 'Comprado!'
                else:
                    msg = 'Sem espaco no inventario!'
        else:  # 'sell'
            slot_index: int | None = None
            for i, slot in enumerate(player.inventory.slots):
                if (
                    slot is not None
                    and slot.name == entry['name']
                    and slot.item_type == 'fruit'
                ):
                    slot_index = i
                    break

            if slot_index is None:
                msg = 'Voce nao tem esse item!'
            else:
                player.inventory.remove_one(slot_index)
                player.nonicoins += entry['price']
                msg = 'Vendido!'

        self._feedback = msg
        self._feedback_timer = self.FEEDBACK_FRAMES
        return msg

    def render(self, screen: pygame.Surface, player: Player) -> None:
        """Renderiza a janela da loja centralizada na tela."""
        # Overlay semitransparente cobrindo a tela toda
        overlay: pygame.Surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill(self.BG_COLOR)
        screen.blit(overlay, (0, 0))

        # Painel central
        panel_x: int = (SCREEN_WIDTH - self.PANEL_WIDTH) // 2
        panel_y: int = (SCREEN_HEIGHT - self.PANEL_HEIGHT) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, self.PANEL_WIDTH, self.PANEL_HEIGHT)

        pygame.draw.rect(screen, self.PANEL_COLOR, panel_rect, border_radius=8)
        pygame.draw.rect(screen, self.PANEL_BORDER, panel_rect, 3, border_radius=8)

        # Titulo
        title_surf: pygame.Surface = self._font_title.render('Trader', True, self.PANEL_BORDER)
        screen.blit(
            title_surf,
            (panel_x + (self.PANEL_WIDTH - title_surf.get_width()) // 2, panel_y + 14)
        )

        # Saldo de Nonicoins
        coins_surf: pygame.Surface = self._font_price.render(
            f'Nonicoins: {player.nonicoins}', True, (255, 215, 0)
        )
        screen.blit(coins_surf, (panel_x + 16, panel_y + 60))

        # Lista de itens do catalogo
        item_start_y: int = panel_y + 98
        item_height: int = 48

        for i, entry in enumerate(self.catalog):
            row_rect = pygame.Rect(
                panel_x + 8,
                item_start_y + i * item_height,
                self.PANEL_WIDTH - 16,
                item_height - 4,
            )

            if i == self.selected_index:
                pygame.draw.rect(screen, self.SELECTED_COLOR, row_rect, border_radius=4)
                pygame.draw.rect(screen, self.PANEL_BORDER, row_rect, 2, border_radius=4)

            action_label: str = 'Comprar' if entry['action'] == 'buy' else 'Vender'
            label: str = f"{action_label}: {entry['name']} ({entry['item_type']})"
            item_surf: pygame.Surface = self._font_item.render(label, True, self.TEXT_COLOR)
            screen.blit(item_surf, (row_rect.x + 10, row_rect.y + 10))

            price_color = (
                self.PRICE_COLOR_BUY if entry['action'] == 'buy' else self.PRICE_COLOR_SELL
            )
            price_surf: pygame.Surface = self._font_price.render(
                f"{entry['price']} NC", True, price_color
            )
            screen.blit(price_surf, (
                row_rect.right - price_surf.get_width() - 10,
                row_rect.y + 12,
            ))

        # Mensagem de feedback (exibida por FEEDBACK_FRAMES frames apos acao)
        if self._feedback_timer > 0:
            self._feedback_timer -= 1
            feedback_surf: pygame.Surface = self._font_feedback.render(
                self._feedback, True, (255, 255, 100)
            )
            screen.blit(feedback_surf, (
                panel_x + (self.PANEL_WIDTH - feedback_surf.get_width()) // 2,
                panel_y + self.PANEL_HEIGHT - 72,
            ))

        # Instrucoes de navegacao
        hint_surf: pygame.Surface = self._font_hint.render(
            'Setas: navegar   Enter: confirmar   Esc: fechar',
            True,
            (160, 140, 100),
        )
        screen.blit(hint_surf, (
            panel_x + (self.PANEL_WIDTH - hint_surf.get_width()) // 2,
            panel_y + self.PANEL_HEIGHT - 34,
        ))
