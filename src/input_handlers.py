from pygame.locals import *
from src.game_states import GameStates


def handle_keys(event, game_state):
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
    
    
def handle_keys_current_turn(event):
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
                return {'special': 'crew'}  # Assign crew screen (repairs, weapons, rowing, sails, etc.)
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
                return {'inventory': 'left'}  # Assign crew screen (repairs, weapons, rowing, sails, etc.)
            elif event.key == K_RIGHT:
                return {'inventory': 'right'}  # Boarding ??  crew for now...
            elif event.key == K_UP:
                return {'inventory': 'up'}  # ramming speed! if player.x == entity.x & player.y == entity.y
            elif event.key == K_DOWN:
                return {'inventory': 'down'}  # drop Mines
            elif event.key == K_SPACE:
                return {'inventory_cancel': True}  # exit inventory
    return {}


def handle_keys_player_dead(event):
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

