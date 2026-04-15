class Animation:
    def __init__(self, clips, initial_state):
        if not clips:
            raise ValueError('Animation clips cannot be empty')
        if initial_state not in clips:
            raise ValueError(f'Initial state "{initial_state}" not found in clips')

        self.clips = clips
        self.current_state = initial_state
        self.frame_index = 0

    def set_state(self, state):
        if state not in self.clips:
            raise ValueError(f'Animation state "{state}" not found in clips')

        if self.current_state != state:
            self.current_state = state
            self.frame_index = 0

    def get_current_frame(self):
        frames = self.clips[self.current_state]
        return frames[self.frame_index]

    def advance_frame(self):
        frames = self.clips[self.current_state]
        if len(frames) <= 1:
            return

        self.frame_index = (self.frame_index + 1) % len(frames)
