from random import randint

import pygame

from components.cargo import Cargo, Item, ItemCategory
from components.crew import Crew
from components.fighter import Fighter
from components.masts import Masts
from components.mobile import Mobile
from components.size import Size
from components.view import View
from components.weapon import WeaponList
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys
from loader_functions.initialize_new_game import get_constants
from map_objects.game_map import make_map, change_wind, adjust_fog
from render_functions import render_display, RenderOrder
from game_time import Time
from weather import Weather, change_weather


def main():
    pygame.init()
    constants = get_constants()
    pygame.key.set_repeat(2, 300)
    global fps_clock
    fps_clock = pygame.time.Clock()
    
    game_time = Time(constants['tick'])
    game_weather = Weather()
    
    display_surface = pygame.display.set_mode((constants['display_width'], constants['display_height']))
    pygame.display.set_caption("Shallow Seas")
    pygame.display.set_icon(constants['icons']['game_icon'])
    
    game_quit = False
    
    message_log = MessageLog(height=constants['log_size'], panel_size=constants['message_panel_size'])
    
    player_icon = constants['icons']['ship_1_mast']
    size_component = Size.MEDIUM
    manifest = []
    manifest.append(Item(name='Canvas', icon=constants['icons']['canvas'], category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Meat', icon=constants['icons']['meat'], category=ItemCategory.SUPPLIES,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Pearls', icon=constants['icons']['pearl'], category=ItemCategory.EXOTICS,
                         weight=0.01, volume=0.01, quantity=30))
    manifest.append(Item(name='Rope', icon=constants['icons']['rope'], category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Rum', icon=constants['icons']['rum'], category=ItemCategory.EXOTICS,
                         weight=0.1, volume=2, quantity=2))
    manifest.append(Item(name='Fish', icon=constants['icons']['fish'], category=ItemCategory.SUPPLIES,
                         weight=0.1, volume=2, quantity=2))
    manifest.append(Item(name='Fruit', icon=constants['icons']['fruit'], category=ItemCategory.SUPPLIES,
                         weight=0.1, volume=2, quantity=2))
    manifest.append(Item(name='Water', icon=constants['icons']['water'], category=ItemCategory.SUPPLIES,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Wood', icon=constants['icons']['wood'], category=ItemCategory.MATERIALS,
                         weight=2, volume=2, quantity=2))
    cargo_component = Cargo(max_volume=size_component.value * 10 + 5,
                            max_weight=size_component.value * 10 + 5,
                            manifest=manifest)
    view_component = View(view=size_component.value + 3)
    fighter_component = Fighter(name="hull", max_hps=size_component.value * 10 + 10)
    weapons_component = WeaponList()
    weapons_component.add_all(size=str(size_component))  # Hacky for now
    mast_component = Masts(name="Mast", masts=size_component.value, size=size_component.value)
    mobile_component = Mobile(direction=0, max_momentum=int(size_component.value) * 2 + 2)
    crew_component = Crew(size=size_component.value, crew_size=50)
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
                    elif attack == 'Arrows' and player.crew.verify_arrow_target(entities=entities):
                        target = True
                    elif player.weapons.verify_target_at_location(attack=attack, entities=entities):
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
                
                # reset game state
                game_state = GameStates.CURRENT_TURN
                
                for entity in entities:
                    if entity.ai:
                        result = entity.ai.take_turn(game_map=game_map,
                                                     target=player,
                                                     message_log=message_log,
                                                     colors=constants['colors'],
                                                     icons=constants['icons'])
                        if result:
                            game_state = GameStates.PLAYER_DEAD
                
                # OTHER ACTIONS ---------------------------------------------------------------------------------------
                # update weapon cool downs - and other things later?
                for entity in entities:
                    if entity.weapons and entity.weapons.weapon_list:
                        for weapon in entity.weapons.weapon_list:
                            if weapon.current_cd > 0:
                                weapon.current_cd -= 1

                # ATTACKS ---------------------------------------------------------------------------------------------
                if attack == 'Arrows':
                    message_log.add_message(message='Player attacks with {}!'.format(attack),
                                            color=constants['colors']['aqua'])
                    player.crew.arrow_attack(terrain=game_map.terrain,
                                             entities=entities,
                                             message_log=message_log,
                                             icons=constants['icons'],
                                             colors=constants['colors'])
                elif attack:
                    message_log.add_message(message='Player attacks to the {}!'.format(attack),
                                            color=constants['colors']['aqua'])
                    player.weapons.attack(terrain=game_map.terrain,
                                          entities=entities,
                                          location=attack,
                                          message_log=message_log,
                                          icons=constants['icons'],
                                          colors=constants['colors'])
                
                # after attacks made, update fog (not before, due to FOV changes)
                game_map.roll_fog(game_time=game_time, game_weather=game_weather)
                
                if other_action:
                    for entity in entities:
                        if not entity.ai and entity.name not in ['player', ''] and \
                                (entity.x, entity.y) == (player.x, player.y):
                            message_log.add_message(message='You salvage the {}'.format(entity.name),
                                                    color=constants['colors']['aqua'])
                            if entity.cargo:
                                for cargo in entity.cargo.manifest:
                                    player.cargo.add_item_to_manifest(item=cargo, message_log=message_log)
                            
                            entity.name = ''
                            entity.icon = None
                            entity.cargo = None
                    
                    if game_map.in_bounds(player.x, player.y) \
                            and game_map.terrain[player.x][player.y].decoration \
                            and game_map.terrain[player.x][player.y].decoration.name == 'Port':
                        message_log.add_message(message='Ahoy! In this port, ye can: trade, repair, hire crew... '
                                                        'or Plunder!',
                                                color=constants['colors']['aqua'])
                
                # MOMENTUM CHANGES ------------------------------------------------------------------------------------
                if slowing:
                    player.mobile.decrease_momentum(amount=slowing, reason='slowing')
                    # message_log.unpack(details=details, color=constants['colors']['text'])
                
                if rowing:
                    player.mobile.rowing = 1
                    # message_log.add_message(message='Rowing...')
                
                # ROWING ----------------------------------------------------------------------------------------------
                for entity in entities:
                    # change momentum due to rowing
                    if entity.mobile and entity.mobile.rowing:
                        if entity.mast_sail:
                            reason = 'rowing'
                        else:
                            reason = 'swimming'
                        details = entity.mobile.increase_momentum(amount=entity.mobile.rowing, reason=reason)
                        if (entity.x, entity.y) in player.view.fov:
                            message_log.unpack(details=details)
                
                # WIND ------------------------------------------------------------------------------------------------
                # adjust speed for wind for each entity with a sail up if there is wind
                if game_map.wind_direction is not None:
                    for entity in entities:
                        if entity.mast_sail and entity.mast_sail.current_sails > 0:
                            details = entity.mast_sail.momentum_due_to_wind(wind_direction=game_map.wind_direction,
                                                                            message_log=message_log,
                                                                            color=constants['colors']['aqua'])
                            for detail in details:
                                if (entity.x, entity.y) in player.view.fov:
                                    message_log.add_message(detail)
                        elif entity.wings and entity.wings.current_wing_power > 0:
                            details = entity.wings.momentum_due_to_wind(wind_direction=game_map.wind_direction,
                                                                        message_log=message_log,
                                                                        color=constants['colors']['aqua'])
                            for detail in details:
                                if (entity.x, entity.y) in player.view.fov:
                                    message_log.add_message(detail)
                
                # DRAG ------------------------------------------------------------------------------------------------
                # change momentum due to drag if not rowing or catching wind
                for entity in entities:
                    drag = - 1
                    if entity.mast_sail and entity.mast_sail.catching_wind:
                        drag = 0
                    if entity.mobile and entity.mobile.rowing:
                        drag = 0
                    if slowing:
                        drag = - 1
                    if entity.mobile:
                        details = entity.mobile.decrease_momentum(amount=drag, reason='drag')
                        for detail in details:
                            if (entity.x, entity.y) in player.view.fov:
                                message_log.add_message(detail)
                    # reset action after drag applied
                    if entity.mast_sail:
                        entity.mast_sail.catching_wind = False
                    if entity.mobile:
                        entity.mobile.rowing = 0
                
                # MOVEMENT --------------------------------------------------------------------------------------------
                for entity in entities:
                    if entity.mobile:
                        details, state = entity.mobile.move(game_map=game_map, player=player)
                        for detail in details:
                            if (entity.x, entity.y) in player.view.fov:
                                message_log.add_message(message=detail, color=constants['colors']['aqua'])
                        if state:
                            game_state = state
                            
                # SAILS / ROTATE --------------------------------------------------------------------------------------
                if sails:
                    details = player.mast_sail.adjust_sails(amount=sails)
                    message_log.unpack(details=details, color=constants['colors']['aqua'])

                # rotate boat last
                if rotate:
                    details = player.mobile.rotate(rotate=rotate)
                    message_log.unpack(details=details, color=constants['colors']['aqua'])

                if exit_screen:
                    game_quit = True
                
                change_wind(game_map=game_map, message_log=message_log, color=constants['colors']['yellow'])
                game_time.roll_min()
                change_weather(weather=game_weather, message_log=message_log, color=constants['colors']['yellow'])
                adjust_fog(fog=game_map.fog,
                           width=game_map.width,
                           height=game_map.height,
                           game_time=game_time,
                           weather=game_weather)
                for entity in entities:
                    if entity.view:
                        entity.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
                message_log.reset_view()
            
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
