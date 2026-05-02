from core.game_manager import GameManager


class Main:
    def __init__(self):
        self.game_manager: GameManager = GameManager()

    def run(self):
        self.game_manager.start()

if __name__ == "__main__":
    main: Main = Main()
    main.run()