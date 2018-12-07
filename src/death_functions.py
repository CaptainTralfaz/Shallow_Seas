from src.game_states import GameStates


def kill_player(player, icons):
    player.icon = icons['sunken_ship']
    return 'You died!', GameStates.PLAYER_DEAD


def kill_monster(monster, icons):
    death_message = '{0} is dead!'.format(monster.name)
    monster.size = None
    monster.icon = icons['carcass']
    monster.view = None
    monster.mobile = None
    monster.ai = None
    monster.fighter = None

    monster.name = 'Dead {}'.format(monster.name)

    return death_message
