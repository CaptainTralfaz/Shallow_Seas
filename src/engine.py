
import pygame

from game_states import GameStates
from input_handlers import handle_keys
from loader_functions.initialize_new_game import get_constants, get_game_variables
from map_objects.game_map import change_wind, adjust_fog, roll_fog
from render_functions import render_display, render_main_menu
from weather import change_weather
from loader_functions.json_loaders import load_game, save_game
from components.cargo import adjust_quantity

def play_game(player, entities, game_map, message_log, game_state, game_weather, game_time, display_surface, constants):
    
    game_quit = False
    pygame.event.clear()

    mouse_x = 0
    mouse_y = 0

    for entity in entities:
        if entity.view:
            entity.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
        if entity.name == 'player':
            player = entity

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
            
            exit_screen = action.get('exit')
            if exit_screen:
                break
            rowing = action.get('rowing')
            slowing = action.get('slowing')
            rotate = action.get('rotate')
            other_action = action.get('other_action')
            scroll = action.get('scroll')
            port = action.get('port')
            increase = action.get('increase')
            decrease = action.get('decrease')
            row_up = action.get('row_up')
            row_down = action.get('row_down')
            repair = action.get('repair')
            
            sails = action.get('sails')
            sails_change = action.get('sails_change')
            if sails_change and player.mast_sail.masts:
                game_state = GameStates.SAILS
            
            attack = action.get('attack')
            targeting = action.get('targeting')
            if targeting:
                game_state = GameStates.TARGETING
            
            special = action.get('special')
            
            # TODO: track precious state ? or just mass "cancel"
            sails_cancel = action.get('sails_cancel')
            target_cancel = action.get('target_cancel')
            special_cancel = action.get('special_cancel')
            inventory_cancel = action.get('inventory_cancel')
            port_cancel = action.get('port_cancel')
            repair_cancel = action.get('repair_cancel')
            
            if sails_cancel or special_cancel or target_cancel or inventory_cancel or port_cancel or repair_cancel:
                game_state = GameStates.CURRENT_TURN

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
            
            if port == "repair":
                game_state = game_state.REPAIR
            elif port == "hire":
                print(port + " not yet implemented")
                game_state = GameStates.CURRENT_TURN
                # game_state = game_state.HIRE
            elif port == "trade":
                print(port + " not yet implemented")
                game_state = GameStates.CURRENT_TURN
                # game_state = game_state.TRADE
            elif port == "upgrade":
                print(port + " not yet implemented")
                game_state = GameStates.CURRENT_TURN
                # game_state = game_state.UPGRADE
            
            if other_action \
                    and game_map.in_bounds(player.x, player.y) \
                    and game_map.terrain[player.x][player.y].decoration \
                    and game_map.terrain[player.x][player.y].decoration.name == 'Port':
                game_state = GameStates.PORT
                message_log.add_message(message='Ahoy! In this port, ye can: trade, repair, or hire crew... ',
                                        color=constants['colors']['aqua'])

            # VERIFY PLAYER ACTION ------------------------------------------------------------------------------------
            
            if repair == "hull":
                # Verify hull is damaged and enough repair materials (wood and tar) exists in cargo
                if player.fighter.hps < player.fighter.max_hps:
                    cargo_name_list = [item.name for item in player.cargo.manifest]
                    missing_items = []
                    for item in player.fighter.repair_with:
                        if item not in cargo_name_list:
                            missing_items.append(item)
                    if missing_items:
                        for item in missing_items:
                            message_log.add_message("Missing {} repair item {} in cargo".format(player.fighter.name,
                                                                                                item))
                        repair = None  # repair attempt failed
                else:
                    message_log.add_message("{} not damaged".format(player.fighter.name))
                    repair = None  # repair attempt failed
            elif repair == "sail":
                # Verify sail exists, is damaged and enough repair materials (canvas and rope) exists in cargo
                if player.mast_sail.max_sails > 0:
                    if player.mast_sail.sail_hp < player.mast_sail.sail_hp_max:
                        cargo_name_list = [item.name for item in player.cargo.manifest]
                        missing_items = []
                        for item in player.mast_sail.sail_repair_with:
                            if item not in cargo_name_list:
                                missing_items.append(item)
                        if missing_items:
                            for item in missing_items:
                                message_log.add_message("Missing sail repair item {} in cargo".format(item))
                            repair = None  # repair attempt failed
                    else:
                        message_log.add_message("Sails not damaged")
                        repair = None  # repair attempt failed
                else:
                    message_log.add_message("No Sails")
                    repair = None  # repair attempt failed
            elif repair == "mast":
                # Verify mast exists, is damaged and enough repair materials (wood and rope) exists in cargo
                if player.mast_sail.masts > 0:
                    if player.mast_sail.mast_hp < player.mast_sail.mast_hp_max:
                        cargo_name_list = [item.name for item in player.cargo.manifest]
                        missing_items = []
                        for item in player.mast_sail.mast_repair_with:
                            if item not in cargo_name_list:
                                missing_items.append(item)
                        if missing_items:
                            for item in missing_items:
                                message_log.add_message("Missing mast repair item {} in cargo".format(item))
                            repair = None  # repair attempt failed
                    else:
                        message_log.add_message("Masts not damaged")
                        repair = None  # repair attempt failed
                else:
                    message_log.add_message("No Masts")
                    repair = None  # repair attempt failed
            elif repair == "weapon":
                # Verify weapon exists, is damaged and enough repair materials (wood and leather) exists in cargo
                print(repair + " not yet implemented")
                repair = None  # repair attempt failed
                game_state = GameStates.CURRENT_TURN

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
            if (rowing or slowing or sails or attack or rotate or other_action or repair) \
                    and not game_state == (GameStates.PLAYER_DEAD and GameStates.PORT):
                
                # reset game state
                game_state = GameStates.CURRENT_TURN
                
                for entity in entities:
                    if entity.ai:
                        result = entity.ai.take_turn(game_map=game_map,
                                                     target=player,
                                                     message_log=message_log,
                                                     colors=constants['colors'])
                        if result:
                            game_state = GameStates.PLAYER_DEAD
                
                # OTHER ACTIONS ---------------------------------------------------------------------------------------
                # update weapon cool downs - and other things later?
                for entity in entities:
                    if entity.weapons and entity.weapons.weapon_list:
                        for weapon in entity.weapons.weapon_list:
                            if weapon.current_cd > 0:
                                weapon.current_cd -= 1
                
                if repair:
                    if repair == "hull":
                        results = player.fighter.heal_damage(1)
                        for result in results:
                            message_log.add_message(message=result, color=constants['colors']['aqua'])
                        for item in player.cargo.manifest:
                            if item.name in player.fighter.repair_with:
                                adjust_quantity(cargo=player.cargo,
                                                item=item,
                                                amount=-1,
                                                message_log=message_log)
                    elif repair == "sail":
                        results = player.mast_sail.repair_sails(1)
                        for result in results:
                            message_log.add_message(message=result, color=constants['colors']['aqua'])
                        for item in player.cargo.manifest:
                            if item.name in player.mast_sail.sail_repair_with:
                                adjust_quantity(cargo=player.cargo,
                                                item=item,
                                                amount=-1,
                                                message_log=message_log)
                    elif repair == "sail":
                        results = player.mast_sail.repair_masts(1)
                        for result in results:
                            message_log.add_message(message=result, color=constants['colors']['aqua'])
                        for item in player.cargo.manifest:
                            if item.name in player.mast_sail.mast_repair_with:
                                adjust_quantity(cargo=player.cargo,
                                                item=item,
                                                amount=-1,
                                                message_log=message_log)
                    elif repair == "weapon":
                        results = player.weapons.repair(1)
                        for result in results:
                            message_log.add_message(message=result, color=constants['colors']['aqua'])
                        for item in player.cargo.manifest:
                            if item.name in player.weapon.repair_with:
                                adjust_quantity(cargo=player.cargo,
                                                item=item,
                                                amount=-1,
                                                message_log=message_log)
                    game_state = GameStates.CURRENT_TURN

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
                roll_fog(game_map=game_map, game_time=game_time, game_weather=game_weather)
                
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
                
                change_wind(game_map=game_map, message_log=message_log, color=constants['colors']['yellow'])
                game_time.roll_min()
                change_weather(weather=game_weather, message_log=message_log, color=constants['colors']['yellow'])
                adjust_fog(terrain=game_map.terrain,
                           width=game_map.width,
                           height=game_map.height,
                           game_time=game_time,
                           weather=game_weather)
                for entity in entities:
                    if entity.view is not None:
                        entity.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
                message_log.reset_view()

                # Save and load every turn for debug purposes
                save_game(player=player, entities=entities, game_map=game_map, message_log=message_log,
                          game_state=game_state,
                          game_weather=game_weather, game_time=game_time)
                player, entities, game_map, message_log, game_state, game_weather, game_time = load_game()
    
                for entity in entities:
                    if entity.view:
                        entity.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
                    if entity.name == 'player':
                        player = entity

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

    # save before quitting
    save_game(player=player, entities=entities, game_map=game_map, message_log=message_log, game_state=game_state,
              game_weather=game_weather, game_time=game_time)
    

def main():
    pygame.init()
    global fps_clock
    fps_clock = pygame.time.Clock()

    constants = get_constants()
    pygame.key.set_repeat(2, 300)

    display_surface = pygame.display.set_mode((constants['display_width'], constants['display_height']))
    pygame.display.set_caption("Shallow Seas")
    pygame.display.set_icon(constants['icons']['game_icon'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = GameStates.MAIN_MENU
    game_weather = None
    game_time = None
    
    show_main_menu = True
    game_quit = False

    render_main_menu(display=display_surface, constants=constants)

    while not game_quit:
        user_input = None
        show_load_error_message = False

        if show_main_menu:
    
            # Get Input -----------------------------------------------------------------------------------------------
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    user_input = event
                    game_quit = True
                    break
                elif event.type == pygame.KEYDOWN:
                    user_input = event
                else:
                    user_input = None
        
            if not user_input:
                continue
        
            if not game_quit:
                
                action = handle_keys(event=user_input, game_state=game_state)
                
                new_game = action.get('new_game')
                load_save = action.get('load_save')
                exit_game = action.get('exit')
    
                if new_game:
                    player, entities, game_map, message_log, game_state, game_weather, game_time = get_game_variables(
                        constants=constants)
                    message_log.add_message("Welcome to Shallow Seas!")
                    show_main_menu = False
                elif load_save:
                    try:
                        player, entities, game_map, message_log, game_state, game_weather, game_time = load_game()
                        show_main_menu = False
                    except FileNotFoundError:
                        show_load_error_message = True
                elif exit_game:
                    game_quit = True
                
                render_main_menu(display=display_surface, constants=constants, error=show_load_error_message)

        else:
            play_game(player=player, entities=entities, game_map=game_map, message_log=message_log,
                      game_state=game_state, game_weather=game_weather, game_time=game_time,
                      display_surface=display_surface, constants=constants)
            show_main_menu = True
            game_state = GameStates.MAIN_MENU
            render_main_menu(display=display_surface, constants=constants, error=show_load_error_message)

    pygame.quit()
    exit()


if __name__ == '__main__':
    main()
