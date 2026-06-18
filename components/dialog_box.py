from __future__ import annotations

import pygame
from enum import Enum, auto
from typing import TYPE_CHECKING

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT

if TYPE_CHECKING:
    from systems.input_system import InputState


class DialogPhase(Enum):
    CLOSED = auto()
    INPUT = auto()
    WAITING = auto()
    RESPONSE = auto()


BOX_MARGIN_X: int = 40
BOX_MARGIN_BOTTOM: int = 20
BOX_HEIGHT: int = 165
BOX_PADDING: int = 14

BOX_COLOR: tuple[int, int, int, int] = (20, 15, 10, 215)
BORDER_COLOR: tuple[int, int, int] = (160, 130, 60)
TEXT_COLOR: tuple[int, int, int] = (255, 245, 200)
NAME_COLOR: tuple[int, int, int] = (255, 215, 0)
HINT_COLOR: tuple[int, int, int] = (140, 120, 80)
INPUT_BG: tuple[int, int, int] = (30, 22, 14)
INPUT_BORDER: tuple[int, int, int] = (100, 80, 40)

TYPEWRITER_CHARS_PER_SEC: float = 40.0

# key_code -> (normal_char, shifted_char)
_KEY_CHARS: dict[int, tuple[str, str]] = {
    **{pygame.K_a + i: (chr(ord('a') + i), chr(ord('A') + i)) for i in range(26)},
    pygame.K_0: ('0', ')'),
    pygame.K_1: ('1', '!'),
    pygame.K_2: ('2', '@'),
    pygame.K_3: ('3', '#'),
    pygame.K_4: ('4', '$'),
    pygame.K_5: ('5', '%'),
    pygame.K_6: ('6', '^'),
    pygame.K_7: ('7', '&'),
    pygame.K_8: ('8', '*'),
    pygame.K_9: ('9', '('),
    pygame.K_SPACE: (' ', ' '),
    pygame.K_PERIOD: ('.', '>'),
    pygame.K_COMMA: (',', '<'),
    pygame.K_MINUS: ('-', '_'),
    pygame.K_SLASH: ('/', '?'),
    pygame.K_SEMICOLON: (';', ':'),
    pygame.K_QUOTE: ("'", '"'),
    pygame.K_EQUALS: ('=', '+'),
}


class DialogBox:
    def __init__(self) -> None:
        self.phase: DialogPhase = DialogPhase.CLOSED
        self.input_text: str = ''
        self._wrapped_lines: list[str] = []
        self._typewriter_progress: float = 0.0
        self._typewriter_total: int = 0
        self._pending_input: str | None = None

        self._font_name: pygame.font.Font = pygame.font.SysFont(None, 30)
        self._font_text: pygame.font.Font = pygame.font.SysFont(None, 26)
        self._font_hint: pygame.font.Font = pygame.font.SysFont(None, 22)

    @property
    def is_open(self) -> bool:
        return self.phase != DialogPhase.CLOSED

    @property
    def has_pending_input(self) -> bool:
        return self._pending_input is not None

    def get_and_clear_pending(self) -> str:
        text: str = self._pending_input or ''
        self._pending_input = None
        return text

    def open(self) -> None:
        self.phase = DialogPhase.INPUT
        self.input_text = ''

    def close(self) -> None:
        self.phase = DialogPhase.CLOSED
        self.input_text = ''
        self._pending_input = None
        self._wrapped_lines = []
        self._typewriter_progress = 0.0

    def show_response(self, text: str) -> None:
        inner_width: int = SCREEN_WIDTH - 2 * BOX_MARGIN_X - 2 * BOX_PADDING
        self._wrapped_lines = self._wrap_text(text, self._font_text, inner_width)
        self._typewriter_total = sum(len(line) for line in self._wrapped_lines)
        self._typewriter_progress = 0.0
        self.phase = DialogPhase.RESPONSE

    def handle_input(self, input_state: InputState) -> None:
        if self.phase == DialogPhase.INPUT:
            self._handle_text_input(input_state)
        elif self.phase == DialogPhase.RESPONSE:
            self._handle_response_input(input_state)

    def _handle_text_input(self, input_state: InputState) -> None:
        if input_state['close_shop']:
            self.close()
            return

        if input_state['confirm'] and self.input_text.strip():
            self._pending_input = self.input_text.strip()
            self.input_text = ''
            self.phase = DialogPhase.WAITING
            return

        just: pygame.key.ScancodeWrapper = pygame.key.get_just_pressed()
        shift: bool = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)

        if just[pygame.K_BACKSPACE]:
            self.input_text = self.input_text[:-1]
            return

        for key_code, (normal, shifted) in _KEY_CHARS.items():
            if just[key_code]:
                self.input_text += shifted if shift else normal

    def _handle_response_input(self, input_state: InputState) -> None:
        if input_state['close_shop']:
            self.close()
            return
        if input_state['confirm'] and self._is_typewriter_done:
            self.close()

    def update(self, dt: float) -> None:
        if self.phase == DialogPhase.RESPONSE:
            self._typewriter_progress = min(
                self._typewriter_progress + TYPEWRITER_CHARS_PER_SEC * dt,
                float(self._typewriter_total),
            )

    @property
    def _is_typewriter_done(self) -> bool:
        return int(self._typewriter_progress) >= self._typewriter_total

    def _wrap_text(
        self,
        text: str,
        font: pygame.font.Font,
        max_width: int,
    ) -> list[str]:
        words: list[str] = text.split(' ')
        lines: list[str] = []
        current: str = ''
        for word in words:
            candidate: str = current + (' ' if current else '') + word
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    # ------------------------------------------------------------------ render

    def render(self, screen: pygame.Surface) -> None:
        if not self.is_open:
            return

        box_x: int = BOX_MARGIN_X
        box_y: int = SCREEN_HEIGHT - BOX_HEIGHT - BOX_MARGIN_BOTTOM
        box_w: int = SCREEN_WIDTH - 2 * BOX_MARGIN_X

        bg: pygame.Surface = pygame.Surface((box_w, BOX_HEIGHT), pygame.SRCALPHA)
        bg.fill(BOX_COLOR)
        screen.blit(bg, (box_x, box_y))
        pygame.draw.rect(screen, BORDER_COLOR, (box_x, box_y, box_w, BOX_HEIGHT), 2)

        name_surf: pygame.Surface = self._font_name.render('Milo:', True, NAME_COLOR)
        screen.blit(name_surf, (box_x + BOX_PADDING, box_y + BOX_PADDING))
        content_y: int = box_y + BOX_PADDING + name_surf.get_height() + 4

        if self.phase == DialogPhase.INPUT:
            self._render_input(screen, box_x, box_y, box_w, content_y)
        elif self.phase == DialogPhase.WAITING:
            self._render_waiting(screen, box_x, box_y, box_w)
        elif self.phase == DialogPhase.RESPONSE:
            self._render_response(screen, box_x, box_y, box_w, content_y)

    def _render_input(
        self,
        screen: pygame.Surface,
        box_x: int,
        box_y: int,
        box_w: int,
        content_y: int,
    ) -> None:
        field_x: int = box_x + BOX_PADDING
        field_w: int = box_w - 2 * BOX_PADDING
        field_h: int = 30
        pygame.draw.rect(screen, INPUT_BG, (field_x, content_y, field_w, field_h))
        pygame.draw.rect(screen, INPUT_BORDER, (field_x, content_y, field_w, field_h), 1)

        display: str = self.input_text + '_'
        text_surf: pygame.Surface = self._font_text.render(display, True, TEXT_COLOR)
        screen.blit(text_surf, (field_x + 4, content_y + 4))

        hint_surf: pygame.Surface = self._font_hint.render(
            'ENTER para enviar  •  ESC para fechar', True, HINT_COLOR
        )
        hint_y: int = box_y + BOX_HEIGHT - BOX_PADDING - hint_surf.get_height()
        screen.blit(hint_surf, (box_x + (box_w - hint_surf.get_width()) // 2, hint_y))

    def _render_waiting(
        self,
        screen: pygame.Surface,
        box_x: int,
        box_y: int,
        box_w: int,
    ) -> None:
        dots_surf: pygame.Surface = self._font_text.render('. . .', True, TEXT_COLOR)
        screen.blit(
            dots_surf,
            (
                box_x + (box_w - dots_surf.get_width()) // 2,
                box_y + (BOX_HEIGHT - dots_surf.get_height()) // 2,
            ),
        )

    def _render_response(
        self,
        screen: pygame.Surface,
        box_x: int,
        box_y: int,
        box_w: int,
        content_y: int,
    ) -> None:
        chars_left: int = int(self._typewriter_progress)
        line_h: int = self._font_text.get_linesize()
        y: int = content_y

        for line in self._wrapped_lines:
            if chars_left <= 0:
                break
            visible: str = line[:chars_left]
            screen.blit(
                self._font_text.render(visible, True, TEXT_COLOR),
                (box_x + BOX_PADDING, y),
            )
            y += line_h
            chars_left -= len(line)

        if self._is_typewriter_done:
            cont_surf: pygame.Surface = self._font_hint.render(
                '[ ENTER para continuar ]', True, HINT_COLOR
            )
            cont_y: int = box_y + BOX_HEIGHT - BOX_PADDING - cont_surf.get_height()
            screen.blit(cont_surf, (box_x + (box_w - cont_surf.get_width()) // 2, cont_y))
