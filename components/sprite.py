import pygame

class Sprite:
    def __init__(self, width, height, path):
        self.width = width
        self.height = height
        self.path = path
        self.surface = pygame.image.load(path)

    def get_path(self):
        return self.path

    def get_size(self):
        return self.width, self.height

    def get_surface(self):
        return self.surface

    def set_surface(self, surface):
        self.surface = surface