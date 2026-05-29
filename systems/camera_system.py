import pygame

class CameraSystem:
    def __init__(
        self,
        screen_width: float,
        screen_height: float,
        world_width: float,
        world_height: float,
    ):
        self.screen_width: float = screen_width
        self.screen_height: float = screen_height
        self.world_width: float = world_width
        self.world_height: float = world_height
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0

    def update(self, target_x: float, target_y: float) -> None:
        self.offset_x = target_x - (self.screen_width / 2)
        self.offset_y = target_y - (self.screen_height / 2)

        max_x: float = max(0, self.world_width - self.screen_width)
        max_y: float = max(0, self.world_height - self.screen_height)

        self.offset_x = max(0.0, min(self.offset_x, max_x))
        self.offset_y = max(0.0, min(self.offset_y, max_y))

    def to_screen(self, world_position: pygame.Vector2) -> pygame.Vector2:
        return pygame.Vector2(
            world_position.x - self.offset_x,
            world_position.y - self.offset_y,
        )
