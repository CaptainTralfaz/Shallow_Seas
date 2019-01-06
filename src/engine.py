from random import randint

import pygame

from src.components.cargo import Cargo, Item, ItemCategory
from src.components.crew import Crew
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
from src.map_objects.game_map import make_map, change_wind, adjust_fog
from src.render_functions import render_display, RenderOrder
from src.time import Time
from src.weather import Weather, change_weather


def main():
    pygame.init()
    constants = get_constants()
    pygame.key.set_repeat(2, 300)
    global fps_clock
    fps_clock = pygame.time.Clock()
    
    game_time = Time()
    game_weather = Weather()
    
    display_surface = pygame.display.set_mode((constants['display_width'], constants['display_height']))
    pygame.display.set_caption("Shallow Seas")
    pygame.display.set_icon(constants['icons']['game_icon'])
    
    game_quit = False
    
    message_log = MessageLog(constants['log_size'], constants['message_panel_size'])
    
    player_icon = constants['icons']['ship_1_mast']
    size_component = Size.SMALL
    manifest = []
    manifest.append(Item(name='Canvas', icon=constants['icons']['canvas'], category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Meat', icon=constants['icons']['meat'], category=ItemCategory.SUPPLIES,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Pearl', icon=constants['icons']['pearl'], category=ItemCategory.EXOTICS,
                         weight=0.01, volume=0.01, quantity=3))
    manifest.append(Item(name='Rope', icon=constants['icons']['rope'], category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Rum', icon=constants['icons']['rum'], category=ItemCategory.EXOTICS,
                         weight=0.1, volume=2, quantity=2))
    manifest.append(Item(name='Water', icon=constants['icons']['water'], category=ItemCategory.SUPPLIES,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Wood', icon=constants['icons']['wood'], category=ItemCategory.MATERIALS,
                         weight=2, volume=2, quantity=2))
    cargo_component = Cargo(capacity=size_component.value * 10 + 5, manifest=manifest)
    view_component = View(view=size_component.value + 3)
    fighter_component = Fighter("hull", size_component.value * 10 + 10)
    weapons_component = WeaponList()
    weapons_component.add_all(size=str(size_component))  # Hacky for now
    mast_component = Masts(name="Mast", masts=size_component.value, size=size_component.value)
    mobile_component = Mobile(direction=0, max_momentum=size_component.value * 2 + 2)
    crew_component = Crew(size=size_component.value, crew=50)
    player = Entity(name='player', x=randint(constants['board_width'] // 4, constants['board_width'] * 3 // 4),
                    y=constants['board_height'] - 1, icon=player_icon, render_order=RenderOrder.PLAYER,
                    view=view_component, size=size_component, mast_sail=mast_component, mobile=mobile_component,
                    weapons=weapons_component, fighter=fighter_component, crew=crew_component, cargo=cargo_component)
    
    entities = [player]
    
    game_map = make_map(width=constants['board_width'],
                        height=constants['board_height'],
                        entities=entities,
                        max_entities=constants['max_entities'],
                        icons=constants['icons'],
                        islands=constants['island_size'],
                        seeds=constants['island_seeds'],
                        constants=constants,
                        game_time=game_time,
                        game_weather=game_weather)
    
    player.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
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
                   game_state=game_state,
                   game_time=game_time,
                   message_log=message_log,
                   game_weather=game_weather)
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
                user_mouse_input = True
                user_input = event
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
            rotate = action.get('rotate')
            other_action = action.get('other_action')
            exit_screen = action.get('exit')
            scroll = action.get('scroll')
            
            sails = action.get('sails')
            sails_change = action.get('sails_change')
            sails_cancel = action.get('sails_cancel')
            if sails_change and player.mast_sail.masts:
                game_state = GameStates.SAILS
            
            attack = action.get('attack')
            targeting = action.get('targeting')
            target_cancel = action.get('target_cancel')
            if targeting:
                game_state = GameStates.TARGETING
            
            special = action.get('special')
            special_cancel = action.get('special_cancel')
            if special:
                game_state = GameStates.SPECIAL
                if special == 'inventory':
                    game_state = GameStates.CARGO
                elif special == 'crew':
                    print(special + " not yet implemented")
                    game_state = GameStates.CURRENT_TURN
                elif special == 'ram':
                    print(special + " not yet implemented")
                    game_state = GameStates.CURRENT_TURN
                elif special == 'mines':
                    print(special + " not yet implemented")
                    game_state = GameStates.CURRENT_TURN
            inventory_cancel = action.get('inventory_cancel')
            
            if sails_cancel or special_cancel or target_cancel or inventory_cancel:
                game_state = GameStates.CURRENT_TURN
            
            # VERIFY PLAYER ACTION ------------------------------------------------------------------------------------
            
            if attack:
                target = False
                # make sure there is a valid target
                if game_map.in_bounds(x=player.x, y=player.y, margin=-1):
                    if game_map.terrain[player.x][player.y].decoration \
                            and game_map.terrain[player.x][player.y].decoration.name == 'Port':
                        target = False
                    elif attack == 'Arrows' and player.crew.verify_arrow_target(entities):
                        target = True
                    elif player.weapons.verify_target_at_location(attack, entities):
                        target = True
                    else:
                        target = None
                if not target:
                    attack = None
            
            if sails:
                if (sails > 0 and player.mast_sail.current_sails == player.mast_sail.max_sails) \
                        or (sails < 0 and player.mast_sail.current_sails == 0):
                    sails = None
            
            # PROCESS ACTION ------------------------------------------------------------------------------------------
            if (rowing or slowing or sails or attack or rotate or other_action) \
                    and not game_state == GameStates.PLAYER_DEAD \
                    or exit_screen:
                
                game_state = GameStates.CURRENT_TURN
                # message_log.adjust_view(len(message_log.messages) - constants['message_panel_size'])
                
                for entity in entities:
                    if entity.ai:
                        result = entity.ai.take_turn(game_map,
                                                     player,
                                                     message_log,
                                                     constants['colors'],
                                                     constants['icons'])
                        if result:
                            game_state = GameStates.PLAYER_DEAD
                
                # OTHER ACTIONS ---------------------------------------------------------------------------------------
                # update weapon cool downs - and other things later?
                for entity in entities:
                    if entity.weapons and entity.weapons.weapon_list:
                        for weapon in entity.weapons.weapon_list:
                            if weapon.current_cd > 0:
                                weapon.current_cd -= 1
                
                if attack == 'Arrows':
                    message_log.add_message('Player attacks with {}!'.format(attack), constants['colors']['aqua'])
                    player.crew.arrow_attack(game_map.terrain, entities, message_log, constants['icons'])
                elif attack:
                    message_log.add_message('Player attacks to the {}!'.format(attack), constants['colors']['aqua'])
                    player.weapons.attack(game_map.terrain, entities, attack, message_log, constants['icons'])
                
                # after attacks made, update fog (not before, due to FOV changes)
                game_map.roll_fog(game_time, game_weather)
                
                if other_action:
                    # for decoration in game_map.decorations:
                    #     if (player.x, player.y) == decoration['location'] and decoration['name'] in ['salvage']:
                    #         message_log.add_message('Grabbed {}!'.format(decoration['name']),
                    #                                 constants['colors']['aqua'])
                    #         game_map.decorations.remove({'name': 'salvage', 'location': (player.x, player.y)})
                    for entity in entities:
                        if not entity.ai and entity.name not in ['player', ''] and \
                                (entity.x, entity.y) == (player.x, player.y):
                            message_log.add_message('You harvest the {}'.format(entity.name),
                                                    constants['colors']['aqua'])
                            if entity.cargo:
                                for cargo in entity.cargo.manifest:
                                    player.cargo.add_item_to_manifest(cargo, message_log)
                            
                            entity.name = ''
                            entity.icon = None
                            entity.cargo = None
                    
                    if game_map.in_bounds(player.x, player.y) \
                            and game_map.terrain[player.x][player.y].decoration \
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
                    if entity.mobile and entity.mobile.rowing and entity.mobile.current_speed < entity.mobile.max_speed:
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
                            message_log.add_message('{} catching Wind, + momentum'.format(entity.name.capitalize()))
                        elif entity.wings and entity.wings.current_wing_power > 0:
                            entity.wings.momentum_due_to_wind(wind_direction=game_map.wind_direction)
                            entity.mast_sail.catching_wind = True
                            message_log.add_message('{} catching Wind, + momentum'.format(entity.name.capitalize()))
                
                # DRAG ------------------------------------------------------------------------------------------------
                # change momentum due to drag if not rowing or catching wind
                for entity in entities:
                    drag = -1
                    if entity.mast_sail and entity.mast_sail.catching_wind:
                        drag = 0
                    elif entity.mobile and entity.mobile.rowing:
                        drag = 0
                    if entity.mobile:
                        entity.mobile.change_momentum(amount=drag)
                    if entity.mast_sail:
                        entity.mast_sail.catching_wind = False
                    if entity.mobile:
                        entity.mobile.rowing = 0
                
                # MOVEMENT --------------------------------------------------------------------------------------------
                for entity in entities:
                    if entity.mobile:
                        old_x = entity.x
                        old_y = entity.y
                        entity.mobile.move(game_map=game_map)
                        if not (entity.x == old_x and entity.y == old_y) \
                                or game_map.wind_direction is not None:  # recalculate fov if entity moved and wind
                            entity.view.set_fov(game_map, game_time, game_weather)
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
                game_time.roll_min()
                change_weather(game_weather, message_log, constants['colors']['yellow'])
                adjust_fog(fog=game_map.fog, width=game_map.width, height=game_map.height,
                           game_time=game_time, weather=game_weather)
            
            elif scroll:
                if constants['map_width'] <= mouse_x < constants['display_width'] \
                        and constants['view_height'] <= mouse_y < constants['display_height']:
                    message_log.adjust_view(scroll)
            
            render_display(display=display_surface,
                           game_map=game_map,
                           player=player,
                           entities=entities,
                           constants=constants,
                           mouse_x=mouse_x,
                           mouse_y=mouse_y,
                           game_state=game_state,
                           game_time=game_time,
                           message_log=message_log,
                           game_weather=game_weather)
            pygame.display.flip()
        
        fps_clock.tick(constants['FPS'])
    
    pygame.quit()
    exit()


if __name__ == '__main__':
    main()
