from src.game_states import GameStates
from src.render_functions import RenderOrder


def kill_player(player, icons):
    """
    Kill the player by changing game state to PLAYER_DEAD and changing the player icon
    :param player: the player entity
    :param icons: a sunken ship
    :return: death message, game state
    """
    player.icon = icons['sunken_ship']
    return 'You have died!', GameStates.PLAYER_DEAD


def kill_monster(entity, icons, elevation=0):
    """
    Kill an entity by changing the entity information and icon
    :param elevation: to see if the creature is on land
    :param entity: the entity that has been killed
    :param icons: carcass icon, used if over water
    :return: death message
    """
    death_message = ['{0} is dead!'.format(entity.name)]
    entity.size = None
    entity.view = None
    entity.mobile = None
    entity.ai = None
    entity.fighter = None
    entity.render_order = RenderOrder.CORPSE
    if elevation < 3:
        entity.name = 'Dead {}'.format(entity.name)
        entity.icon = icons['carcass']
    else:
        entity.name = ''
        entity.icon = None
    
    return death_message
