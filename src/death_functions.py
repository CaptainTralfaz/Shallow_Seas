from src.game_states import GameStates
from src.render_functions import RenderOrder


def kill_player(player, icons):
    player.icon = icons['sunken_ship']
    return 'You died!', GameStates.PLAYER_DEAD


def kill_monster(entity, icons):
    death_message = '{0} is dead!'.format(entity.name)
    entity.size = None
    entity.icon = icons['carcass']
    entity.view = None
    entity.mobile = None
    entity.ai = None
    entity.fighter = None
    entity.render_order = RenderOrder.CORPSE

    entity.name = 'Dead {}'.format(entity.name)

    return death_message
