from enum import Enum


class GameStates(Enum):
    CURRENT_TURN = 1
    TARGETING = 2
    PLAYER_DEAD = 3
    SAILS = 4
