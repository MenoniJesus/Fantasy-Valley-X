import pygame
from typing import Sequence, TypedDict


class InputState(TypedDict):
	move_up: bool
	move_down: bool
	move_left: bool
	move_right: bool
	sprint: bool
	axe: bool
	hoe: bool
	toggle_debug: bool


class InputSystem:
	def __init__(self):
		pass

	def read(self, events: Sequence[pygame.event.Event]):
		keys = pygame.key.get_pressed()

		input_state: InputState = {
			'move_up': keys[pygame.K_w],
			'move_down': keys[pygame.K_s],
			'move_left': keys[pygame.K_a],
			'move_right': keys[pygame.K_d],
			'sprint': keys[pygame.K_LSHIFT],
			'axe': False,
			'hoe': False,
			'toggle_debug': False,
		}

		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					input_state['axe'] = True
				if event.key == pygame.K_e:
					input_state['hoe'] = True
				if event.key == pygame.K_h:
					input_state['toggle_debug'] = True

		return input_state
