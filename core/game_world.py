import pygame
from pytmx.util_pygame import load_pygame

from entities.entity import Entity
from entities.player import Player
from entities.world import World
from entities.static_objects import StaticObject

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
        self.debug_colliders: bool = True

        # Cria e adiciona entidade do mundo
        self.world = World()
        self.add_entity(self.world)
        self.world.start_music()

        # Cria e adiciona entidade do player
        self.player = Player(self.world.spawn)
        self.add_entity(self.player)
        self._player_prev_pos: tuple[float, float] = self.player.get_position()

        # Cria os objetos estáticos do mapa
        self.load_static_objects()

        self.camera_system = CameraSystem(
            self.screen.get_width(),
            self.screen.get_height(),
            self.world.rect.width,
            self.world.rect.height,
        )

    def load_static_objects(self):
        tmx_data = load_pygame('assets/map/map.tmx')
        
        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            static_object = StaticObject(
                name='Tree',
                position=(obj.x, obj.y),
                surface=obj.image
            )
            
            self.add_entity(static_object)
            
        # Decoration
        for obj in tmx_data.get_layer_by_name('Decoration'):
            static_object = StaticObject(
                name='Decoration',
                position=(obj.x, obj.y),
                surface=obj.image
            )
            
            self.add_entity(static_object)

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

        if self.debug_colliders:
            self._draw_colliders()

    def _draw_colliders(self):
        debug_color = (255, 0, 0)

        for entity in self.entities:
            colliders = self.collision_system.get_colliders(entity)
            for collider in colliders:
                rect = collider.get_rect()
                screen_x, screen_y = self.camera_system.to_screen((rect.x, rect.y))
                debug_rect = pygame.FRect(screen_x, screen_y, rect.width, rect.height)
                pygame.draw.rect(self.screen, debug_color, debug_rect, 2)

    def collision_process(self):
        for entity_a in self.entities:
            for entity_b in self.entities:
                if entity_a is entity_b:
                    continue

                is_collision = self.collision_system.check_colliders(
                    entity_a,
                    entity_b
                )
                
                if (is_collision and entity_a.name == 'player') or (is_collision and entity_b.name == 'player'):
                    if (isinstance(entity_a, Player)):
                        pass
                    elif (isinstance(entity_b, Player)):
                        pass
 
    def handle_events(self, input_state: InputState):
        if input_state['use_tool']:
            if self.player.tool_in_use == 0: # Hoe
                self.player.cut_grass()
                
            elif self.player.tool_in_use == 1: # Axe
                pass
            
            elif self.player.tool_in_use == 2: # Watering Can
                pass
        
        if input_state['toggle_debug']:
            self.debug_colliders = not self.debug_colliders