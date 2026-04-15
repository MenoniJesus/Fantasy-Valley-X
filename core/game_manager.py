import pygame

from core.settings import *
from core.world_game import WorldGame
from systems.input_system import InputSystem

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Fantasy Valley')
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.input_system = InputSystem()
        self.worldGame = WorldGame(self.screen)

    def start(self):
        while self.running:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            input_state = self.input_system.read(events)
            self.update(input_state)

    def update(self, input_state):
        self.dt = self.clock.tick(60) / 1000
        self.worldGame.handle_events(input_state)
        self.worldGame.update(self.dt, input_state)
        
    def __del__(self):
        pygame.quit()