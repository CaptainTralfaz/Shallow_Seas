from src.game_states import GameStates


def kill_player(player, constants):
    player.icon = constants['icons']['sunken_ship']

    return 'You died!', GameStates.PLAYER_DEAD


def kill_monster(monster, constants):
    death_message = '{0} is dead!'.format(monster.name)
    monster.size = None
    monster.icon = constants['icons']['sunken_ship']
    monster.view = None
    monster.mobile = None
    monster.ai = None
    monster.fighter = None

    monster.name = 'Remains of ' + monster.name

    return death_message
