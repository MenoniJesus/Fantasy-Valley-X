import pygame

from core.settings import *
from core.game_world import WorldGame
from systems.input_system import InputState, InputSystem

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Fantasy Valley')
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.dt: float = 0.0
        self.input_system: InputSystem = InputSystem()
        self.worldGame: WorldGame = WorldGame(self.screen)

    def start(self):
        while self.running:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            input_state = self.input_system.read(events)
            self.update(input_state)

    def update(self, input_state: InputState):
        self.dt = self.clock.tick(60) / 1000
        self.worldGame.handle_events(input_state)
        self.worldGame.update(self.dt, input_state)

    def __del__(self):
        pygame.quit()