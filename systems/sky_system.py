import pygame

from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class SkySystem:
    def __init__(self) -> None:
        self.day_number: int = 1

        # Ciclo dia/noite
        self.day_duration: float = 120.0  # segundos de um dia completo
        self.elapsed: float = 0.0         # tempo decorrido no dia atual
        self.overlay_alpha: int = 0       # 0 = dia claro, 180 = noite escura

        # Overlay de escurecimento
        self.overlay: pygame.Surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.overlay.fill((0, 0, 0))

    def update(self, dt: float) -> None:
        """Atualiza o tempo do dia."""
        self.elapsed += dt
        progress: float = self.elapsed / self.day_duration

        if progress < 0.5:
            self.overlay_alpha = 0
        else:
            self.overlay_alpha = int((progress - 0.5) * 2 * 180)

        if self.overlay_alpha > 180:
            self.overlay_alpha = 180

    def render(self, screen: pygame.Surface) -> None:
        """Renderiza overlay de noite sobre a tela."""
        self.overlay.set_alpha(self.overlay_alpha)
        screen.blit(self.overlay, (0, 0))

    def advance_day(self) -> None:
        """Avança para o próximo dia."""
        self.day_number += 1
        self.elapsed = 0.0
        self.overlay_alpha = 0

    def is_near_bed(
        self,
        player_pos: pygame.Vector2,
        bed_pos: pygame.Vector2,
        threshold: float = 80.0,
    ) -> bool:
        """Retorna True se o player estiver próximo da cama."""
        return (player_pos - bed_pos).length() < threshold
