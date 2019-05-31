from game_states import GameStates


class Game:
    def __init__(self, game_time=None, travels=0):
        self.game_time = game_time
        self.travels = travels
        self.state = GameStates(0)
