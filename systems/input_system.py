import pygame
from typing import Sequence, TypedDict


class InputState(TypedDict):
	move_up: bool
	move_down: bool
	move_left: bool
	move_right: bool
	sprint: bool
	toggle_debug: bool
	use_tool: bool
	next_day: bool
	sleep: bool
	plant: bool
	arrow_up: bool
	arrow_down: bool
	confirm: bool
	close_shop: bool
	selected_slot: int | None


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
			'toggle_debug': False,
			'use_tool': False,
			'next_day': False,
			'sleep': False,
			'plant': False,
			'arrow_up': False,
			'arrow_down': False,
			'confirm': False,
			'close_shop': False,
			'selected_slot': None,
		}

		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_h:
					input_state['toggle_debug'] = True

				if event.key == pygame.K_e:
					input_state['use_tool'] = True

				if event.key == pygame.K_n:
					input_state['next_day'] = True

				if event.key == pygame.K_z:
					input_state['sleep'] = True

				if event.key == pygame.K_f:
					input_state['plant'] = True

				if event.key == pygame.K_RETURN:
					input_state['confirm'] = True

				if event.key == pygame.K_ESCAPE:
					input_state['close_shop'] = True

				if event.key == pygame.K_UP:
					input_state['arrow_up'] = True

				if event.key == pygame.K_DOWN:
					input_state['arrow_down'] = True

				# Teclas 1–9 selecionam slots 0–8
				if pygame.K_1 <= event.key <= pygame.K_9:
					input_state['selected_slot'] = event.key - pygame.K_1

		return input_state
