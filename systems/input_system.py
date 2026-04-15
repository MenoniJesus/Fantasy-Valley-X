import pygame


class InputSystem:
	def __init__(self):
		pass

	def read(self, events):
		keys = pygame.key.get_pressed()

		input_state = {
			'move_up': keys[pygame.K_w],
			'move_down': keys[pygame.K_s],
			'move_left': keys[pygame.K_a],
			'move_right': keys[pygame.K_d],
			'sprint': keys[pygame.K_LSHIFT],
			'axe': False,
			'hoe': False,
		}

		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					input_state['axe'] = True
				if event.key == pygame.K_e:
					input_state['hoe'] = True

		return input_state
