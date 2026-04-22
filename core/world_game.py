import pygame

from entities.entity import Entity
from entities.player import Player
from entities.world import World

from systems.collision_system import CollisionSystem
from systems.render_system import RenderSystem
from systems.sound_system import SoundSystem
from systems.camera_system import CameraSystem
from systems.input_system import InputState


class WorldGame:
    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen
        self.entities: list[Entity] = []

        self.last_direction: str = 'down'
        self.animation_counter: int = 0
        self.animation_step: int = 10

        self.sound_system: SoundSystem = SoundSystem()
        self.render_system: RenderSystem = RenderSystem(self.screen)
        self.collision_system: CollisionSystem = CollisionSystem()

        self.world = World()
        self.add_entity(self.world)
        self.world.start_music()

        spawn = (screen.get_width() / 2, screen.get_height() / 2)
        self.player = Player(spawn)
        self.add_entity(self.player)

        self.camera_system = CameraSystem(
            self.screen.get_width(),
            self.screen.get_height(),
            self.world.rect.width,
            self.world.rect.height,
        )

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def _resolve_animation_state(self, input_state: InputState):
        moving = (
            input_state['move_up'] or input_state['move_down']
            or input_state['move_left'] or input_state['move_right']
        )

        if input_state['move_up']:
            self.last_direction = 'up'
        elif input_state['move_down']:
            self.last_direction = 'down'
        elif input_state['move_left']:
            self.last_direction = 'left'
        elif input_state['move_right']:
            self.last_direction = 'right'

        if moving:
            return f'walk_{self.last_direction}'

        return f'idle_{self.last_direction}'

    def _update_player_animation(self, input_state: InputState):
        animation = self.player.get_component('animation')
        target_state = self._resolve_animation_state(input_state)
        animation.set_state(target_state)

        self.animation_counter += 1
        if self.animation_counter >= self.animation_step:
            animation.advance_frame()
            self.animation_counter = 0

        current_frame = animation.get_current_frame()
        self.player.get_component('sprite').set_surface(current_frame)

    def _move_player(self, dt: float, input_state: InputState):
        speed = 350 if input_state['sprint'] else 250
        self.player.set_speed(speed)

        move_x = 0.0
        move_y = 0.0

        if input_state['move_up']:
            move_y -= self.player.speed * dt
        if input_state['move_down']:
            move_y += self.player.speed * dt
        if input_state['move_left']:
            move_x -= self.player.speed * dt
        if input_state['move_right']:
            move_x += self.player.speed * dt

        self.player.move(move_x, move_y)
        self._clamp_player_to_world()

    def _clamp_player_to_world(self):
        max_x = max(0, self.world.rect.width - self.player.rect.width)
        max_y = max(0, self.world.rect.height - self.player.rect.height)

        self.player.rect.x = max(0, min(self.player.rect.x, max_x))
        self.player.rect.y = max(0, min(self.player.rect.y, max_y))

    def _update_camera(self):
        target_x = self.player.rect.centerx
        target_y = self.player.rect.centery
        self.camera_system.update(target_x, target_y)

    def update(self, dt: float, input_state: InputState):
        self._move_player(dt, input_state)
        self._update_player_animation(input_state)
        self._update_camera()
        self.collision_process()

        self.screen.fill((0, 0, 0))
        self.render(dt)
        pygame.display.flip()

    def render(self, dt: float):
        for entity in self.entities:
            sprite = entity.get_component('sprite')
            if sprite is None:
                continue

            self.render_system.render(sprite, entity.get_position(), self.camera_system)

    def collision_process(self):
        collisions: list[tuple[Entity, Entity]] = []

        for entity_a in self.entities:
            for entity_b in self.entities:
                if entity_a is entity_b:
                    continue

                if self.collision_system.are_entities_colliding(entity_a, entity_b):
                    collisions.append((entity_a, entity_b))

        return collisions


    def handle_events(self, input_state: InputState):
        if input_state['axe']:
            self.sound_system.play_sound(self.player.get_component('axe_sound'))
        if input_state['hoe']:
            self.sound_system.play_sound(self.player.get_component('hoe_sound'))