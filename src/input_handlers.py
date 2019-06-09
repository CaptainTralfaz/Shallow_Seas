from pygame.locals import *

from game_states import GameStates


def handle_keys(event, game_state):
    """
    Translates user interactions into code commands depending on the state of the game
    :param event: list of interactions
    :param game_state: determines which command set to forward interactions to
    :return: dict of key presses and meaning depending on state
    """
    if game_state == GameStates.CURRENT_TURN:
        return handle_keys_current_turn(event)
    elif game_state == GameStates.TARGETING:
        return handle_keys_targeting(event)
    elif game_state == GameStates.SAILS:
        return handle_keys_adjust_sails(event)
    elif game_state == GameStates.SPECIAL:
        return handle_keys_special(event)
    elif game_state == GameStates.CARGO:
        return handle_keys_cargo(event)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_keys_player_dead(event)
    elif game_state == GameStates.MAIN_MENU:
        return handle_keys_main_menu(event)
    elif game_state == GameStates.PORT:
        return handle_keys_port(event)
    elif game_state == GameStates.REPAIR:
        return handle_keys_repair(event)
    # elif game_state == GameStates.TRADE:
    #     return handle_keys_trade(event)
    # elif game_state == GameStates.HIRE:
    #     return handle_keys_hire(event)
    # elif game_state == GameStates.UPGRADE:
    #     return handle_keys_upgrade_menu(event)


def handle_keys_current_turn(event):
    """
    Interaction translation for standard CURRENT_TURN events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit the game
            return {'exit': True}
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key in [309, 310]:  # Mac command keys
                return {'targeting': True}
            elif event.key in [303, 304]:
                return {'sails_change': True}
            elif event.key in [307, 308]:
                return {'special': True}
            elif event.key == K_LEFT:
                return {'rotate': 1}
            elif event.key == K_RIGHT:
                return {'rotate': -1}
            elif event.key == K_UP:
                return {'rowing': 1}
            elif event.key == K_DOWN:
                return {'slowing': -1}
            elif event.key == K_SPACE:
                return {'other_action': True}
    return {}


def handle_keys_targeting(event):
    """
    Interaction translation for TARGETING events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit Targeting state
            return {'target_cancel': True}
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_LEFT:
                return {'attack': 'Port'}
            elif event.key == K_RIGHT:
                return {'attack': 'Starboard'}
            elif event.key == K_UP:
                return {'attack': 'Bow'}
            elif event.key == K_DOWN:
                return {'attack': 'Stern'}
            elif event.key == K_SPACE:
                return {'attack': 'Arrows'}  # Arrow Attack
            elif event.key in [309, 310]:  # Mac command keys
                return {'target_cancel': True}
    return {}


def handle_keys_adjust_sails(event):
    """
    Interaction translation for SAILS events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit the Adjust Sails state
            return {'sails_cancel': True}
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_UP:
                return {'sails': 1}
            elif event.key == K_DOWN:
                return {'sails': -1}
            elif event.key in [303, 304]:  # Mac command keys
                return {'sails_cancel': True}
    return {}


def handle_keys_special(event):
    """
    Interaction translation for SPECIAL action events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit Special Keys state
            return {'special_cancel': True}
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_LEFT:
                return {'special': 'crew'}  # Crew Action (Put out fire?)
            elif event.key == K_RIGHT:
                return {'special': 'crew'}  # Boarding ??  crew for now...
            elif event.key == K_UP:
                return {'special': 'ram'}  # ramming speed! if player.x == entity.x & player.y == entity.y
            elif event.key == K_DOWN:
                return {'special': 'mines'}  # drop Mines
            elif event.key == K_SPACE:
                return {'special': 'inventory'}  # inventory screen
            elif event.key in [307, 308]:
                return {'special_cancel': True}
    return {}


def handle_keys_cargo(event):
    """
    Interaction translation for CARGO screen events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit Special Keys state
            return {'inventory_cancel': True}  # exit inventory
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_LEFT:
                return {'inventory': 'left'}  # amount +
            elif event.key == K_RIGHT:
                return {'inventory': 'right'}  # amount -
            elif event.key == K_UP:
                return {'inventory': 'up'}  # move row selection up
            elif event.key == K_DOWN:
                return {'inventory': 'down'}  # move row selection down
            elif event.key == K_SPACE:
                return {'inventory_cancel': True}  # exit inventory
    return {}


def handle_keys_port(event):
    """
    Interaction translation for PORT screen events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit Special Keys state
            return {'port_cancel': True}  # exit port
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_LEFT:
                return {'port': 'repair'}  # repair menu
            elif event.key == K_RIGHT:
                return {'port': 'hire'}  # hire menu
            elif event.key == K_UP:
                return {'port': 'trade'}  # trade menu
            elif event.key == K_DOWN:
                return {'port': 'upgrade'}  # upgrade menu
            elif event.key == K_SPACE:
                return {'port_cancel': True}  # exit port
    return {}


def handle_keys_repair(event):
    """
    Interaction translation for REPAIR screen events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit Special Keys state
            return {'repair_cancel': True}  # exit repair
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_LEFT:
                return {'repair': 'hull'}  # repair menu
            elif event.key == K_RIGHT:
                return {'repair': 'weapon'}  # hire menu
            elif event.key == K_UP:
                return {'repair': 'sail'}  # trade menu
            elif event.key == K_DOWN:
                return {'repair': 'mast'}  # upgrade menu
            elif event.key == K_SPACE:
                return {'repair_cancel': True}  # exit repair
    return {}


def handle_keys_player_dead(event):
    """
    Interaction translation for PLAYER_DEAD events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit the game
            return {'exit': True}
        
        if event.type == MOUSEBUTTONDOWN:
            if event.button in [5]:
                return {'scroll': 1}
            elif event.button in [4]:
                return {'scroll': -1}
        
        # if event.type == KEYDOWN:
        # mac command  mod L:1024 R:2048  key L:310 R:309
        # mac option   mod L:256  R:512   key L:308 R:307
        # mac shift    mod L:1    R:2     key L:304 R:303
        # if event.key in [307, 308]:
        #     return {'special': True}
    return {}


def handle_keys_main_menu(event):
    """
    Interaction translation for MAIN_MENU events
    :param event: list of interactions
    :return: translated command in dict form
    """
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit the game
            return {'exit': True}
        
        if event.type == KEYDOWN:
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_LEFT:
                return {'new_game': True}   # Start new game
            elif event.key == K_RIGHT:
                return {'load_save': True}  # Load old game

    return {}
