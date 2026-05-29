from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from core.inventory import Inventory
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from entities.player import Player


class HudSystem:
    SLOT_SIZE: int = 64
    SLOT_PADDING: int = 6
    SLOT_COLOR: tuple[int, int, int] = (50, 50, 50)
    SLOT_BORDER: tuple[int, int, int] = (120, 120, 120)
    SLOT_SELECTED: tuple[int, int, int] = (255, 215, 0)
    TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)
    COINS_COLOR: tuple[int, int, int] = (0, 0, 0)

    def __init__(self) -> None:
        self._font: pygame.font.Font = pygame.font.SysFont(None, 20)
        self._font_coins: pygame.font.Font = pygame.font.SysFont(None, 28)

    def render(self, screen: pygame.Surface, inventory: Inventory, player: Player) -> None:
        """Renderiza a hotbar centralizada na parte inferior da tela."""
        total_width: int = (
            Inventory.SLOTS * (self.SLOT_SIZE + self.SLOT_PADDING) - self.SLOT_PADDING
        )
        start_x: int = (SCREEN_WIDTH - total_width) // 2
        start_y: int = SCREEN_HEIGHT - self.SLOT_SIZE - 16

        for i, item in enumerate(inventory.slots):
            slot_x: int = start_x + i * (self.SLOT_SIZE + self.SLOT_PADDING)
            slot_rect = pygame.Rect(slot_x, start_y, self.SLOT_SIZE, self.SLOT_SIZE)

            # Fundo do slot
            pygame.draw.rect(screen, self.SLOT_COLOR, slot_rect)

            # Borda: dourada se selecionado, cinza caso contrário
            if i == inventory.selected_index:
                pygame.draw.rect(screen, self.SLOT_SELECTED, slot_rect, 3)
            else:
                pygame.draw.rect(screen, self.SLOT_BORDER, slot_rect, 1)

            if item is None:
                continue

            # Ícone centralizado no slot
            if item.icon is not None:
                icon_x: int = slot_x + (self.SLOT_SIZE - 48) // 2
                icon_y: int = start_y + (self.SLOT_SIZE - 48) // 2
                screen.blit(item.icon, (icon_x, icon_y))

            # Quantidade no canto inferior direito (apenas se > 1)
            if item.quantity > 1:
                qty_surf: pygame.Surface = self._font.render(
                    str(item.quantity), True, self.TEXT_COLOR
                )
                qty_x: int = slot_x + self.SLOT_SIZE - qty_surf.get_width() - 4
                qty_y: int = start_y + self.SLOT_SIZE - qty_surf.get_height() - 4
                screen.blit(qty_surf, (qty_x, qty_y))

        # Saldo de Nonicoins no canto superior direito
        coins_surf: pygame.Surface = self._font_coins.render(
            f'Nonicoins: {player.nonicoins}', True, self.COINS_COLOR
        )
        screen.blit(coins_surf, (SCREEN_WIDTH - coins_surf.get_width() - 16, 16))
