from random import randint

import pygame

from src.components.masts import Masts
from src.components.mobile import Mobile
from src.components.size import Size
from src.components.view import View
from src.entity import Entity
from src.input_handlers import handle_keys
from src.loader_functions.initialize_new_game import get_constants
from src.map_objects.game_map import make_map, change_wind
from src.render_functions import render_display
from src.game_messages import MessageLog


def main():
    pygame.init()
    constants = get_constants()
    pygame.key.set_repeat(2, 300)
    global fps_clock
    fps_clock = pygame.time.Clock()
    
    display_surface = pygame.display.set_mode((constants['display_width'], constants['display_height']))
    pygame.display.set_caption("Shallow Seas")
    pygame.display.set_icon(constants['icons']['game_icon'])
    
    game_quit = False
    
    message_log = MessageLog(constants['log_size'])
    
    size_component = Size(2)
    view_component = View(size_component.size + 3)
    mast_component = Masts(name="Mast", masts=2, size=size_component.size)
    mobile_component = Mobile(direction=0, max_momentum=size_component.size * 2 + 2)
    player_icon = constants['icons']['ship_1_mast']
    player = Entity(name='player', x=randint(constants['board_width'] // 4, constants['board_width'] * 3 // 4),
                    y=constants['board_height'] - 1, icon=player_icon, view=view_component, size=size_component,
                    mast_sail=mast_component, mobile=mobile_component)
    
    entities = []
    
    game_map = make_map(constants['board_width'],
                        constants['board_height'],
                        entities,
                        constants['max_entities'],
                        constants['icons'],
                        constants['island_size'],
                        constants['island_seeds'])
    
    player.view.set_fov(game_map)
    
    mouse_x = 0
    mouse_y = 0
    
    render_display(display=display_surface,
                   game_map=game_map,
                   player=player,
                   entities=entities,
                   constants=constants,
                   mouse_x=mouse_x,
                   mouse_y=mouse_y,
                   message_log=message_log)
    
    pygame.display.flip()
    
    # Main Loop -------------------------------------------------------------------------------------------------------
    while not game_quit:
        user_input = None
        user_mouse_input = None
        
        # Get Input ---------------------------------------------------------------------------------------------------
        event_list = pygame.event.get()
        for event in event_list:
            
            if event.type == pygame.QUIT:
                user_input = event
                game_quit = True
                break
            elif event.type == pygame.KEYDOWN:
                user_input = event
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                user_mouse_input = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                user_mouse_input = event
                break
            else:
                user_input = None
                user_mouse_input = None
        
        if not (user_input or user_mouse_input):
            continue
        
        if not game_quit:
            
            action = handle_keys(event=user_input)
            
            rowing = action.get('rowing')
            slowing = action.get('slowing')
            sails = action.get('sails')
            attack = action.get('attack')
            rotate = action.get('rotate')
            other_action = action.get('other_action')
            exit_screen = action.get('exit')
            targeting = action.get('targeting')
            
            # PROCESS ACTION ------------------------------------------------------------------------------------------
            if rowing or slowing or sails or attack or rotate or other_action or exit_screen:

                for entity in entities:
                    if entity.ai:
                        entity.ai.take_turn(game_map, player, message_log, constants['colors'])
                
                # OTHER ACTIONS ---------------------------------------------------------------------------------------
                if attack:
                    message_log.add_message('Player attacks {}!'.format(attack),
                                            constants['colors']['aqua'])
                
                if other_action:
                    # for decoration in game_map.decorations:
                    #     if (player.x, player.y) == decoration['location'] and decoration['name'] in ['salvage']:
                    #         message_log.add_message('Grabbed {}!'.format(decoration['name']),
                    #                                 constants['colors']['aqua'])
                    #         game_map.decorations.remove({'name': 'salvage', 'location': (player.x, player.y)})
                    if game_map.terrain[player.x][player.y].decoration \
                            and game_map.terrain[player.x][player.y].decoration.name == 'Town':
                        message_log.add_message('Ahoy! In this town, ye can: trade, repair, hire crew... or Plunder!',
                                                constants['colors']['aqua'])
                
                # MOMENTUM CHANGES ------------------------------------------------------------------------------------
                if rowing:
                    player.mobile.rowing = 1
                    message_log.add_message('Rowing, +1 momentum')
                    
                if slowing:
                    player.mobile.change_momentum(amount=slowing)
                    message_log.add_message('Slowing, -1 momentum', constants['colors']['aqua'])
                
                # ROWING ----------------------------------------------------------------------------------------------
                if player.mobile.rowing and player.mobile.current_speed < player.mobile.max_speed:
                    player.mobile.change_momentum(amount=player.mobile.rowing)
                    # check to make sure a ship can't go to max speed
                    if player.mobile.current_speed == player.mobile.max_speed:
                        player.mobile.current_speed -= 1
                        player.mobile.current_momentum = player.mobile.max_momentum
                
                for entity in entities:
                    # change momentum due to rowing
                    if entity.mobile.rowing and entity.mobile.current_speed < entity.mobile.max_speed:
                        entity.mobile.change_momentum(amount=entity.mobile.rowing)
                        # if (entity.x, entity.y) in player.view.fov:
                        #     message_log.add_message('{} at {}:{} momentum {}'.format(entity.name,
                        #                                                              entity.x,
                        #                                                              entity.y,
                        #                                                              entity.mobile.rowing))
                        
                        # check to make sure a ship can't go to max speed
                        if hasattr(entity, 'mast_sail') \
                                and entity.mobile.current_speed == entity.mobile.max_speed:
                            entity.mobile.current_speed -= 1
                            entity.mobile.current_momentum = entity.mobile.max_momentum
                
                # WIND ------------------------------------------------------------------------------------------------
                # adjust speed for wind for each entity with a sail up if there is wind
                if game_map.wind_direction is not None:
                    if hasattr(player, "mast_sail") and player.mast_sail.current_sails > 0:
                        amount = player.mast_sail.momentum_due_to_wind(wind_direction=game_map.wind_direction)
                        player.mast_sail.catching_wind = True
                        if amount:
                            message_log.add_message('Catching Wind, {} momentum'.format(amount),
                                                    constants['colors']['green'])

                # adjust speed for wind for each entity with a sail up if there is wind
                if game_map.wind_direction is not None:
                    for entity in entities:
                        if hasattr(entity, "mast_sail") and entity.mast_sail.current_sails > 0:
                            entity.mast_sail.momentum_due_to_wind(wind_direction=game_map.wind_direction)
                            entity.mast_sail.catching_wind = True
                            message_log.add_message('Catching Wind, + momentum')

                # DRAG ------------------------------------------------------------------------------------------------
                # change momentum due to drag if not rowing or catching wind
                
                drag = -1
                if player.mast_sail.catching_wind or player.mobile.rowing:
                    drag = 0
                player.mobile.change_momentum(amount=drag)
                player.mast_sail.catching_wind = False
                player.mobile.rowing = 0
                
                for entity in entities:
                    drag = -1
                    if hasattr(entity, "mast_sail") and entity.mast_sail.catching_wind:
                        drag = 0
                    elif entity.mobile.rowing:
                        drag = 0
                    entity.mobile.change_momentum(amount=drag)
                    if hasattr(entity, "mast_sail"):
                        entity.mast_sail.catching_wind = False
                    entity.mobile.rowing = 0
                
                # MOVEMENT --------------------------------------------------------------------------------------------
                # move all entities with a current_speed
                old_x = player.x
                old_y = player.y
                player.mobile.move(game_map=game_map)
                if not (player.x == old_x and player.y == old_y):  # recalculate fov if entity moved
                    player.view.set_fov(game_map)
                
                for entity in entities:
                    if hasattr(entity, 'mobile'):
                        old_x = entity.x
                        old_y = entity.y
                        entity.mobile.move(game_map=game_map)
                        if not (entity.x == old_x and entity.y == old_y):  # recalculate fov if entity moved
                            entity.view.set_fov(game_map)
                            # print("{} moved to {}:{}".format(entity.name, entity.x, entity.y))
                
                # SAILS / ROTATE --------------------------------------------------------------------------------------
                if sails:
                    player.mast_sail.adjust_sails(amount=sails)
                    message_log.add_message('Player Adjusts sails to {}'.format(player.mast_sail.current_sails),
                                            constants['colors']['aqua'])

                # rotate boat last
                if rotate:
                    player.mobile.rotate(rotate=rotate)
                    message_log.add_message('Player rotates {}'.format('port' if rotate == 1 else 'starboard'))

                if exit_screen:
                    game_quit = True
                
                change_wind(game_map, message_log, constants['colors']['yellow'])
            
            render_display(display=display_surface,
                           game_map=game_map,
                           player=player,
                           entities=entities,
                           constants=constants,
                           mouse_x=mouse_x,
                           mouse_y=mouse_y,
                           targeting=targeting,
                           message_log=message_log)
            pygame.display.flip()
        
        fps_clock.tick(constants['FPS'])
    
    pygame.quit()
    exit()


if __name__ == '__main__':
    main()
