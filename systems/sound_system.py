import pygame

from components.sound import Sound


class SoundSystem:
    def __init__(self):
        pass

    def play_sound(self, sound: Sound | str, volume: float = 1.0):
        if isinstance(sound, Sound):
            sound_path: str = sound.path
        else:
            sound_path = sound

        sfx: pygame.mixer.Sound = pygame.mixer.Sound(sound_path)
        sfx.set_volume(volume)
        sfx.play()