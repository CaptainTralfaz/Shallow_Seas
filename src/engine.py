from random import randint

import pygame

from src.components.fighter import Fighter
from src.components.masts import Masts
from src.components.mobile import Mobile
from src.components.size import Size
from src.components.view import View
from src.components.weapon import WeaponList
from src.entity import Entity
from src.game_messages import MessageLog
from src.game_states import GameStates
from src.input_handlers import handle_keys
from src.loader_functions.initialize_new_game import get_constants
from src.map_objects.game_map import make_map, change_wind
from src.map_objects.map_utils import get_target_hexes_at_location
from src.render_functions import render_display


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
    
    player_icon = constants['icons']['ship_1_mast']
    size_component = Size.TINY
    view_component = View(view=size_component.value + 3)
    fighter_component = Fighter("hull", size_component.value * 10 + 5)
    weapons_component = WeaponList()
    weapons_component.add_all(size=str(size_component))  # Hacky for now
    mast_component = Masts(name="Mast", masts=size_component.value, size=size_component.value)
    mobile_component = Mobile(direction=0, max_momentum=size_component.value * 2 + 2)
    player = Entity(name='player', x=randint(constants['board_width'] // 4, constants['board_width'] * 3 // 4),
                    y=constants['board_height'] - 1, icon=player_icon, view=view_component, size=size_component,
                    mast_sail=mast_component, mobile=mobile_component, weapons=weapons_component,
                    fighter=fighter_component)
    
    entities = [player]
    
    game_map = make_map(constants['board_width'],
                        constants['board_height'],
                        entities,
                        constants['max_entities'],
                        constants['icons'],
                        constants['island_size'],
                        constants['island_seeds'])
    
    player.view.set_fov(game_map)
    game_state = GameStates.CURRENT_TURN
    
    mouse_x = 0
    mouse_y = 0
    
    render_display(display=display_surface,
                   game_map=game_map,
                   player=player,
                   entities=entities,
                   constants=constants,
                   mouse_x=mouse_x,
                   mouse_y=mouse_y,
                   message_log=message_log,
                   game_state=game_state)
    
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
            
            action = handle_keys(event=user_input, game_state=game_state)
            
            rowing = action.get('rowing')
            slowing = action.get('slowing')
            sails = action.get('sails')
            attack = action.get('attack')
            rotate = action.get('rotate')
            other_action = action.get('other_action')
            exit_screen = action.get('exit')
            targeting = action.get('targeting')
            if targeting:
                game_state = GameStates.TARGETING
            
            # VERIFY PLAYER ACTION ------------------------------------------------------------------------------------
            
            if attack:
                # make sure there is a target
                weapon_list = player.weapons.get_weapons_at_location(attack)
                if len(weapon_list) > 0:  # make sure there is a weapon on that side
                    attack_range = weapon_list[0].max_range
                    target_hexes = get_target_hexes_at_location(player, attack, attack_range)
                    valid_target = False
                    for entity in entities:
                        if (entity.x, entity.y) in target_hexes:
                            valid_target = True
                    if not valid_target:  # no targets in range
                        attack = None
                else:
                    attack = None  # no weapons at that location
            if sails:
                if (sails > 0 and player.mast_sail.current_sails == player.mast_sail.max_sails) \
                        or (sails < 0 and player.mast_sail.current_sails == 0):
                    sails = None
            
            # PROCESS ACTION ------------------------------------------------------------------------------------------
            if rowing or slowing or sails or attack or rotate or other_action or exit_screen:
                
                game_state = GameStates.CURRENT_TURN
                
                for entity in entities:
                    if entity.ai:
                        entity.ai.take_turn(game_map, player, message_log, constants['colors'])
                
                # OTHER ACTIONS ---------------------------------------------------------------------------------------
                if attack:
                    player.weapons.attack(entities, attack, message_log)
                    message_log.add_message('Player attacks to the {}!'.format(attack),
                                            constants['colors']['aqua'])
                
                if other_action:
                    # for decoration in game_map.decorations:
                    #     if (player.x, player.y) == decoration['location'] and decoration['name'] in ['salvage']:
                    #         message_log.add_message('Grabbed {}!'.format(decoration['name']),
                    #                                 constants['colors']['aqua'])
                    #         game_map.decorations.remove({'name': 'salvage', 'location': (player.x, player.y)})
                    if game_map.terrain[player.x][player.y].decoration \
                            and game_map.terrain[player.x][player.y].decoration.name == 'Port':
                        message_log.add_message('Ahoy! In this port, ye can: trade, repair, hire crew... or Plunder!',
                                                constants['colors']['aqua'])
                
                # MOMENTUM CHANGES ------------------------------------------------------------------------------------
                if rowing:
                    player.mobile.rowing = 1
                    message_log.add_message('Rowing, +1 momentum')
                
                if slowing:
                    player.mobile.change_momentum(amount=slowing)
                    message_log.add_message('Slowing, -1 momentum', constants['colors']['aqua'])
                
                # ROWING ----------------------------------------------------------------------------------------------
                for entity in entities:
                    # change momentum due to rowing
                    if entity.mobile.rowing and entity.mobile.current_speed < entity.mobile.max_speed:
                        entity.mobile.change_momentum(amount=entity.mobile.rowing)
                        # check to make sure a ship can't go to max speed
                        if entity.mast_sail and entity.mobile.current_speed == entity.mobile.max_speed:
                            entity.mobile.current_speed -= 1
                            entity.mobile.current_momentum = entity.mobile.max_momentum
                
                # WIND ------------------------------------------------------------------------------------------------
                # adjust speed for wind for each entity with a sail up if there is wind
                if game_map.wind_direction is not None:
                    for entity in entities:
                        if entity.mast_sail and entity.mast_sail.current_sails > 0:
                            entity.mast_sail.momentum_due_to_wind(wind_direction=game_map.wind_direction)
                            entity.mast_sail.catching_wind = True
                            message_log.add_message('Catching Wind, + momentum')
                
                # DRAG ------------------------------------------------------------------------------------------------
                # change momentum due to drag if not rowing or catching wind
                for entity in entities:
                    drag = -1
                    if entity.mast_sail and entity.mast_sail.catching_wind:
                        drag = 0
                    elif entity.mobile.rowing:
                        drag = 0
                    entity.mobile.change_momentum(amount=drag)
                    if entity.mast_sail:
                        entity.mast_sail.catching_wind = False
                    entity.mobile.rowing = 0
                
                # MOVEMENT --------------------------------------------------------------------------------------------
                for entity in entities:
                    if entity.mobile:
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
                           game_state=game_state,
                           message_log=message_log)
            pygame.display.flip()
        
        fps_clock.tick(constants['FPS'])
    
    pygame.quit()
    exit()


if __name__ == '__main__':
    main()
