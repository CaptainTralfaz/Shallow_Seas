from pygame.locals import *
from src.game_states import GameStates


def handle_keys(event, game_state):
    if game_state == GameStates.CURRENT_TURN:
        return handle_keys_current_turn(event)
    elif game_state == GameStates.TARGETING:
        return handle_keys_targeting(event)
    elif game_state == GameStates.SAILS:
        return handle_keys_adjust_sails(event)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_keys_player_dead(event)
    
    
def handle_keys_current_turn(event):
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit the game
            return {'exit': True}
        # scroll up: 5    <Event(5-MouseButtonDown {'pos': (369, 713), 'button': 5})>
        # scroll down: 4  <Event(5-MouseButtonDown {'pos': (369, 713), 'button': 4})>
        
        if event.type == MOUSEBUTTONDOWN:
            # print("Mouse Button Down")
            # print(event)
            if event.button in [5]:
                # print('scroll up')
                return {'scroll': 1}
            elif event.button in [4]:
                # print('scroll down')
                return {'scroll': -1}

        if event.type == KEYDOWN:
            # print(event)
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key in [309, 310]:  # Mac command keys
                return {'targeting': True}
            elif event.key in [303, 304]:
                return {'sails_change': True}
            elif event.key == K_LEFT and event.mod in [256, 512]:
                return {'special': 'left'}
            elif event.key == K_RIGHT and event.mod in [256, 512]:
                return {'special': 'right'}
            elif event.key == K_UP and event.mod in [256, 512]:
                return {'special': 'up'}
            elif event.key == K_DOWN and event.mod in [256, 512]:
                return {'special': 'down'}
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
            # Exit the game
            return {'target_cancel': True}

        if event.type == MOUSEBUTTONDOWN:
            # print("Mouse Button Down")
            # print(event)
            if event.button in [5]:
                # print('scroll up')
                return {'scroll': 1}
            elif event.button in [4]:
                # print('scroll down')
                return {'scroll': -1}

        if event.type == KEYDOWN:
            # print(event)
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
            elif event.key in [309, 310]:  # Mac command keys
                return {'target_cancel': True}
    return {}


def handle_keys_adjust_sails(event):
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit the game
            return {'sails_cancel': True}
        
        if event.type == MOUSEBUTTONDOWN:
            # print("Mouse Button Down")
            # print(event)
            if event.button in [5]:
                # print('scroll up')
                return {'scroll': 1}
            elif event.button in [4]:
                # print('scroll down')
                return {'scroll': -1}

        if event.type == KEYDOWN:
            # print(event)
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


def handle_keys_player_dead(event):
    if event:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            # Exit the game
            return {'exit': True}
        
        if event.type == MOUSEBUTTONDOWN:
            # print("Mouse Button Down")
            # print(event)
            if event.button in [5]:
                # print('scroll up')
                return {'scroll': 1}
            elif event.button in [4]:
                # print('scroll down')
                return {'scroll': -1}

        if event.type == KEYDOWN:
            # print(event)
            # mac command  mod L:1024 R:2048  key L:310 R:309
            # mac option   mod L:256  R:512   key L:308 R:307
            # mac shift    mod L:1    R:2     key L:304 R:303
            if event.key == K_LEFT and event.mod in [256, 512]:
                return {'special': 'left'}
            elif event.key == K_RIGHT and event.mod in [256, 512]:
                return {'special': 'right'}
            elif event.key == K_UP and event.mod in [256, 512]:
                return {'special': 'up'}
            elif event.key == K_DOWN and event.mod in [256, 512]:
                return {'special': 'down'}
            elif event.key == K_UP and event.mod in [1, 2]:
                return {'sails': 1}
            elif event.key == K_DOWN and event.mod in [1, 2]:
                return {'sails': -1}
    return {}

