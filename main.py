import pygame

from components.sprite import Sprite

from entities.entity import Entity
from systems.render_system import RenderSystem

pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

player_pos = pygame.Vector2(
    screen.get_width() / 2,
    screen.get_height() / 2
)

# Criar componentes e entidade FORA do loop
player_sprite = Sprite(20, 20)
player = Entity(player_pos, [player_sprite])

render_system = RenderSystem(screen)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    render_system.render(player)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()