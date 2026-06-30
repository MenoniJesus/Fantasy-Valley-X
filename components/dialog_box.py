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
BOX_HEIGHT: int = 250
BOX_PADDING: int = 16
PORTRAIT_SIZE: int = 96
BORDER_RADIUS: int = 16

BOX_X: int = BOX_MARGIN_X
BOX_W: int = SCREEN_WIDTH - 2 * BOX_MARGIN_X
BOX_Y: int = SCREEN_HEIGHT - BOX_HEIGHT - BOX_MARGIN_BOTTOM

CONTENT_X: int = BOX_X + BOX_PADDING + PORTRAIT_SIZE + BOX_PADDING
CONTENT_W: int = BOX_X + BOX_W - BOX_PADDING - CONTENT_X

BOX_BG: tuple[int, int, int, int] = (62, 41, 26, 235)
BORDER_COLOR: tuple[int, int, int] = (224, 173, 92)
BORDER_COLOR_DARK: tuple[int, int, int] = (122, 80, 42)
SHADOW_COLOR: tuple[int, int, int, int] = (0, 0, 0, 100)
TEXT_COLOR: tuple[int, int, int] = (255, 244, 214)
NAME_COLOR: tuple[int, int, int] = (255, 210, 96)
HINT_COLOR: tuple[int, int, int] = (200, 172, 116)
INPUT_BG: tuple[int, int, int] = (44, 29, 18)
INPUT_BORDER: tuple[int, int, int] = (170, 128, 64)
PORTRAIT_BG: tuple[int, int, int] = (34, 22, 14)

TYPEWRITER_CHARS_PER_SEC: float = 40.0

_RETRO_FONT_CANDIDATES: str = 'Cascadia Mono,Consolas,Lucida Console,Courier New'


def _load_retro_font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont(_RETRO_FONT_CANDIDATES, size, bold=bold)


def _make_portrait(source: pygame.Surface, size: int) -> pygame.Surface:
    canvas: pygame.Surface = pygame.Surface((size, size), pygame.SRCALPHA)
    canvas.fill(PORTRAIT_BG)
    scale: float = min(size / source.get_width(), size / source.get_height())
    w: int = max(1, int(source.get_width() * scale))
    h: int = max(1, int(source.get_height() * scale))
    scaled: pygame.Surface = pygame.transform.smoothscale(source, (w, h))
    canvas.blit(scaled, ((size - w) // 2, (size - h) // 2))
    return canvas


class DialogBox:
    def __init__(self, portrait: pygame.Surface | None = None) -> None:
        self.phase: DialogPhase = DialogPhase.CLOSED
        self.input_text: str = ''
        self._lines: list[str] = []
        self._line_offsets: list[int] = []
        self._scroll_offset: int = 0
        self._typewriter_progress: float = 0.0
        self._typewriter_total: int = 0
        self._pending_input: str | None = None

        self._font_name: pygame.font.Font = _load_retro_font(26, bold=True)
        self._font_text: pygame.font.Font = _load_retro_font(40)
        self._font_hint: pygame.font.Font = _load_retro_font(18)

        self._portrait: pygame.Surface | None = (
            _make_portrait(portrait, PORTRAIT_SIZE) if portrait is not None else None
        )

        available_h: int = (
            BOX_HEIGHT
            - 2 * BOX_PADDING
            - self._font_name.get_linesize()
            - 6
            - self._font_hint.get_linesize()
            - 6
        )
        self._visible_lines: int = max(1, available_h // self._font_text.get_linesize())

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
        pygame.key.start_text_input()

    def close(self) -> None:
        self.phase = DialogPhase.CLOSED
        self.input_text = ''
        self._pending_input = None
        self._lines = []
        self._line_offsets = []
        self._scroll_offset = 0
        self._typewriter_progress = 0.0
        pygame.key.stop_text_input()

    def show_response(self, text: str) -> None:
        self._lines = self._wrap_text(text, self._font_text, CONTENT_W) or ['']

        self._line_offsets = []
        offset: int = 0
        for line in self._lines:
            self._line_offsets.append(offset)
            offset += len(line) + 1

        self._typewriter_total = offset
        self._typewriter_progress = 0.0
        self._scroll_offset = 0
        self.phase = DialogPhase.RESPONSE

    def _active_line_index(self) -> int:
        progress: int = int(self._typewriter_progress)
        index: int = 0
        for i, line_offset in enumerate(self._line_offsets):
            if progress > line_offset:
                index = i
            else:
                break
        return index

    @property
    def _max_scroll(self) -> int:
        return max(0, len(self._lines) - self._visible_lines)

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

        if input_state['backspace']:
            self.input_text = self.input_text[:-1]

        self.input_text += input_state['text_input']

    def _handle_response_input(self, input_state: InputState) -> None:
        if input_state['close_shop']:
            self.close()
            return
        if input_state['arrow_up']:
            self._scroll_offset = max(0, self._scroll_offset - 1)
        if input_state['arrow_down']:
            self._scroll_offset = min(self._max_scroll, self._scroll_offset + 1)
        if input_state['confirm'] and self._is_typewriter_done:
            self._return_to_input()

    def _return_to_input(self) -> None:
        self.phase = DialogPhase.INPUT
        self.input_text = ''
        self._lines = []
        self._line_offsets = []
        self._scroll_offset = 0
        self._typewriter_progress = 0.0

    def update(self, dt: float) -> None:
        if self.phase == DialogPhase.RESPONSE:
            self._typewriter_progress = min(
                self._typewriter_progress + TYPEWRITER_CHARS_PER_SEC * dt,
                float(self._typewriter_total),
            )
            if not self._is_typewriter_done:
                active_line: int = self._active_line_index()
                if active_line >= self._scroll_offset + self._visible_lines:
                    self._scroll_offset = min(
                        self._max_scroll, active_line - self._visible_lines + 1
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
        lines: list[str] = []
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append('')
                continue

            words: list[str] = paragraph.split(' ')
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

        self._render_panel(screen)

        name_surf: pygame.Surface = self._font_name.render('Milo', True, NAME_COLOR)
        screen.blit(name_surf, (CONTENT_X, BOX_Y + BOX_PADDING))
        content_y: int = BOX_Y + BOX_PADDING + name_surf.get_height() + 6

        if self.phase == DialogPhase.INPUT:
            self._render_input(screen, content_y)
        elif self.phase == DialogPhase.WAITING:
            self._render_waiting(screen)
        elif self.phase == DialogPhase.RESPONSE:
            self._render_response(screen, content_y)

    def _render_panel(self, screen: pygame.Surface) -> None:
        shadow: pygame.Surface = pygame.Surface((BOX_W, BOX_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(shadow, SHADOW_COLOR, (0, 0, BOX_W, BOX_HEIGHT), border_radius=BORDER_RADIUS)
        screen.blit(shadow, (BOX_X + 6, BOX_Y + 6))

        panel: pygame.Surface = pygame.Surface((BOX_W, BOX_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(panel, BOX_BG, (0, 0, BOX_W, BOX_HEIGHT), border_radius=BORDER_RADIUS)
        screen.blit(panel, (BOX_X, BOX_Y))

        pygame.draw.rect(
            screen, BORDER_COLOR, (BOX_X, BOX_Y, BOX_W, BOX_HEIGHT),
            width=3, border_radius=BORDER_RADIUS,
        )
        pygame.draw.rect(
            screen, BORDER_COLOR_DARK,
            (BOX_X + 4, BOX_Y + 4, BOX_W - 8, BOX_HEIGHT - 8),
            width=1, border_radius=BORDER_RADIUS - 3,
        )

        if self._portrait is not None:
            port_x: int = BOX_X + BOX_PADDING
            port_y: int = BOX_Y + BOX_PADDING
            pygame.draw.rect(
                screen, PORTRAIT_BG, (port_x, port_y, PORTRAIT_SIZE, PORTRAIT_SIZE),
                border_radius=10,
            )
            screen.blit(self._portrait, (port_x, port_y))
            pygame.draw.rect(
                screen, BORDER_COLOR, (port_x, port_y, PORTRAIT_SIZE, PORTRAIT_SIZE),
                width=2, border_radius=10,
            )

    def _render_input(self, screen: pygame.Surface, content_y: int) -> None:
        field_h: int = 32
        pygame.draw.rect(
            screen, INPUT_BG, (CONTENT_X, content_y, CONTENT_W, field_h), border_radius=6,
        )
        pygame.draw.rect(
            screen, INPUT_BORDER, (CONTENT_X, content_y, CONTENT_W, field_h),
            width=1, border_radius=6,
        )

        display: str = self.input_text
        max_w: int = CONTENT_W - 10
        while display and self._font_text.size(display)[0] > max_w:
            display = display[1:]
        display += '_'

        text_surf: pygame.Surface = self._font_text.render(display, True, TEXT_COLOR)
        screen.blit(text_surf, (CONTENT_X + 6, content_y + 5))

        hint_surf: pygame.Surface = self._font_hint.render(
            'ENTER para enviar  •  ESC para fechar', True, HINT_COLOR
        )
        hint_y: int = BOX_Y + BOX_HEIGHT - BOX_PADDING - hint_surf.get_height()
        screen.blit(hint_surf, (CONTENT_X + (CONTENT_W - hint_surf.get_width()) // 2, hint_y))

    def _render_waiting(self, screen: pygame.Surface) -> None:
        dots_surf: pygame.Surface = self._font_text.render('. . .', True, TEXT_COLOR)
        screen.blit(
            dots_surf,
            (
                CONTENT_X + (CONTENT_W - dots_surf.get_width()) // 2,
                BOX_Y + (BOX_HEIGHT - dots_surf.get_height()) // 2,
            ),
        )

    def _render_response(self, screen: pygame.Surface, content_y: int) -> None:
        progress: int = int(self._typewriter_progress)
        line_h: int = self._font_text.get_linesize()
        y: int = content_y
        visible_end: int = min(self._scroll_offset + self._visible_lines, len(self._lines))

        for i in range(self._scroll_offset, visible_end):
            line: str = self._lines[i]
            revealed: int = max(0, min(len(line), progress - self._line_offsets[i]))
            if revealed <= 0 and progress <= self._line_offsets[i]:
                break
            if line: 
                screen.blit(
                    self._font_text.render(line[:revealed], True, TEXT_COLOR),
                    (CONTENT_X, y),
                )
            y += line_h

        if self._is_typewriter_done:
            can_scroll: bool = len(self._lines) > self._visible_lines
            hint_text: str = (
                '↑↓ rolar  •  ENTER continuar  •  ESC fechar' if can_scroll
                else 'ENTER para continuar  •  ESC para fechar'
            )
            hint_surf: pygame.Surface = self._font_hint.render(hint_text, True, HINT_COLOR)
            hint_y: int = BOX_Y + BOX_HEIGHT - BOX_PADDING - hint_surf.get_height()
            screen.blit(hint_surf, (CONTENT_X + (CONTENT_W - hint_surf.get_width()) // 2, hint_y))