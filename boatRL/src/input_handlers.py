from pygame.locals import *


def handle_keys(event):
    if event:
        if event.key == K_ESCAPE:
            # Exit the game
            return {'exit': True}
        
        if event.type == KEYDOWN:
            # print(event)
            if event.key == K_LEFT and event.mod in [1024, 2048]:
                return {'attack': 'port'}
            elif event.key == K_RIGHT and event.mod in [1024, 2048]:
                return {'attack': 'starboard'}
            elif event.key == K_UP and event.mod in [1024, 2048]:
                return {'attack': 'fore'}
            elif event.key == K_DOWN and event.mod in [1024, 2048]:
                return {'attack': 'aft'}
            elif event.key in [309, 310]:  # Mac command keys
                return {'targeting': True}
            elif event.key == K_UP and event.mod in [1, 2]:
                return {'sails': 1}
            elif event.key == K_DOWN and event.mod in [1, 2]:
                return {'sails': -1}
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
