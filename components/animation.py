import pygame


class Animation:
    def __init__(self, clips: dict[str, list[pygame.Surface]], initial_state: str):
        self.clips: dict[str, list[pygame.Surface]] = clips
        self.current_state: str = initial_state
        self.frame_index: int = 0

    def set_state(self, state: str):
        if self.current_state != state:
            self.current_state = state
            self.frame_index = 0

    def get_current_frame(self):
        frames: list[pygame.Surface] = self.clips[self.current_state]
        return frames[self.frame_index]

    def advance_frame(self):
        frames: list[pygame.Surface] = self.clips[self.current_state]
        if len(frames) <= 1:
            return

        self.frame_index = (self.frame_index + 1) % len(frames)
