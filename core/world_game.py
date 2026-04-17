import pygame

from entities.background import Background
from entities.player import Player

from systems.render_system import RenderSystem
from systems.sound_system import SoundSystem
from systems.camera_system import CameraSystem

class WorldGame:
    def __init__(self, screen):
        self.screen = screen
        self.last_direction = 'down'
        self.animation_counter = 0
        self.animation_step = 10
        self.sound_system = SoundSystem()
        self.render_system = RenderSystem(self.screen)

        # Background
        self.background = Background()
        background_size = self.background.components['sprite'].get_size()
        self.camera_system = CameraSystem(
            self.screen.get_width(),
            self.screen.get_height(),
            background_size[0],
            background_size[1],
        )
        self.music_bg = pygame.mixer.music.load('assets/sounds/music/music.mp3')
        pygame.mixer.music.play(loops=-1)
        
        # Player
        spawn = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        self.player = Player(spawn)

    def _resolve_animation_state(self, input_state):
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

    def _update_player_animation(self, input_state):
        animation = self.player.components['animation']
        target_state = self._resolve_animation_state(input_state)
        animation.set_state(target_state)

        self.animation_counter += 1
        if self.animation_counter >= self.animation_step:
            animation.advance_frame()
            self.animation_counter = 0

        current_frame = animation.get_current_frame()
        self.player.components['sprite'].set_surface(current_frame)

    def update(self, dt, input_state):        
        speed = 350 if input_state['sprint'] else 250

        self.player.components['velocity'].set_velocity(speed)

        if input_state['move_up']:
            self.player.position_Y -= speed * dt
        if input_state['move_down']:
            self.player.position_Y += speed * dt
        if input_state['move_left']:
            self.player.position_X -= speed * dt
        if input_state['move_right']:
            self.player.position_X += speed * dt

        self._update_player_animation(input_state)

        player_width, player_height = self.player.components['sprite'].get_size()
        target_x = self.player.position_X + (player_width / 2)
        target_y = self.player.position_Y + (player_height / 2)
        self.camera_system.update(target_x, target_y)
        
        # Background
        self.render_system.render(self.background.components['sprite'], self.background.get_position(), self.camera_system)

        # Player
        self.render_system.render(self.player.components['sprite'], self.player.get_position(), self.camera_system)
        
        pygame.display.flip()
        
    def handle_events(self, input_state):
        if input_state['axe']:
            self.sound_system.play_sound(self.player.components['axe_sound'])
        if input_state['hoe']:
            self.sound_system.play_sound(self.player.components['hoe_sound'])