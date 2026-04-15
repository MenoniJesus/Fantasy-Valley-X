class CameraSystem:
	def __init__(self, screen_width, screen_height, world_width, world_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.world_width = world_width
		self.world_height = world_height
		self.offset_x = 0
		self.offset_y = 0

	def update(self, target_x, target_y):
		self.offset_x = target_x - (self.screen_width / 2)
		self.offset_y = target_y - (self.screen_height / 2)

		max_x = max(0, self.world_width - self.screen_width)
		max_y = max(0, self.world_height - self.screen_height)

		self.offset_x = max(0, min(self.offset_x, max_x))
		self.offset_y = max(0, min(self.offset_y, max_y))

	def to_screen(self, world_position):
		return (world_position[0] - self.offset_x, world_position[1] - self.offset_y)
