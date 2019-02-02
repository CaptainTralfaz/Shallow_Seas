from enum import Enum


class GameStates(Enum):
    """
    Holds the state of the game
    """
    MAIN_MENU = 0
    CURRENT_TURN = 1
    TARGETING = 2
    PLAYER_DEAD = 3
    SAILS = 4
    SPECIAL = 5
    CARGO = 6
