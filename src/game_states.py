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
    PORT = 7
    REPAIR = 8
    TRADE = 9
    HIRE = 10
    UPGRADE = 11
