import math
from enum import Enum

import pygame

from game_states import GameStates
from map_objects.map_utils import direction_angle, get_grid_from_coords, get_target_hexes, get_hex_neighbors
from map_objects.tile import Elevation


class RenderOrder(Enum):
    TERRAIN = 0
    DECORATION = 1
    CORPSE = 2
    FLOATING = 3
    SWIMMING = 4
    PLAYER = 5
    FLYING = 6
    FOG = 7


def render_display(display, game_map, player, entities,
                   constants, mouse_x, mouse_y, message_log, game_state, game_time, game_weather):
    """
    Draw the game: Status panel, Mini Map, messages, controls, GameBoard / Cargo Manifest
    :param display: The main display window surface
    :param game_map: the GameMap object
    :param player: Player entity
    :param entities: other actors
    :param constants: dict game constants
    :param mouse_x: int x coordinate of mouse
    :param mouse_y: int y coordinate of mouse
    :param message_log: list of messages for display
    :param game_state: current enum game state
    :param game_time: current game Time object
    :param game_weather: current game Weather object
    :return: None
    """
    display.fill(constants['colors']['black'])
    
    # draw and blit mini-map
    map_surf = render_map(game_map=game_map,
                          player=player,
                          entities=entities,
                          constants=constants)
    display.blit(map_surf, (0, 0))
    
    # draw and blit status panel
    status_surf = render_status(player=player,
                                constants=constants)
    display.blit(status_surf, (0, constants['map_height'] + constants['control_height']))
    
    # draw and blit available controls
    control_surf = render_control(game_map=game_map,
                                  player=player,
                                  entities=entities,
                                  constants=constants,
                                  game_state=game_state)
    display.blit(control_surf, (0, constants['map_height']))
    
    # draw and blit game messages
    message_surf = render_messages(message_log=message_log,
                                   constants=constants)
    display.blit(message_surf, (constants['status_width'], constants['view_height']))
    
    # draw and blit cargo manifest
    if game_state == GameStates.CARGO:
        inventory_surf = render_manifest(cargo=player.cargo,
                                         constants=constants)
        display.blit(inventory_surf, (constants['map_width'], 0))
    else:
        # draw and blit game play area
        board_surf = render_board(game_map=game_map,
                                  player=player,
                                  entities=entities,
                                  constants=constants,
                                  game_state=game_state,
                                  game_time=game_time,
                                  game_weather=game_weather)
        display.blit(board_surf, (constants['map_width'], 0))
        
        # Draw and blit info under mouse, but now out of bounds
        info_surf = get_info_under_mouse(game_map=game_map,
                                         player=player,
                                         entities=entities,
                                         mouse_x=mouse_x,
                                         mouse_y=mouse_y,
                                         constants=constants)
        if info_surf:
            location_x = mouse_x + constants['half_tile']
            location_y = mouse_y + constants['half_tile']
            if location_x + info_surf.get_width() > constants['display_width'] - constants['margin']:
                location_x = constants['display_width'] - constants['margin'] - info_surf.get_width()
            if location_y + info_surf.get_height() > constants['view_height'] - constants['margin']:
                location_y = constants['view_height'] - constants['margin'] - info_surf.get_height()
            display.blit(info_surf, (location_x, location_y))
    
    pygame.display.update()


def render_manifest(cargo, constants):
    """
    Render the manifest in the main display
    :param cargo: Cargo component
    :param constants: constants
    :return: None
    """
    inventory_surf = pygame.Surface((constants['view_width'] - 2 * constants['margin'],
                                     constants['view_height'] - 2 * constants['margin']))
    inventory_surf.fill(constants['colors']['dark_gray'])
    
    vertical = constants['margin']
    vertical = render_cargo_header(inventory_surf=inventory_surf, vertical=vertical, constants=constants)
    vertical = render_cargo(inventory_surf=inventory_surf, cargo=cargo, vertical=vertical, constants=constants)
    vertical = render_cargo_totals(inventory_surf=inventory_surf, cargo=cargo, vertical=vertical, constants=constants)
    
    border_panel = pygame.Surface((constants['view_width'], constants['view_height']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    border_panel.blit(inventory_surf, (constants['margin'], constants['margin']))
    return border_panel


def render_cargo_header(inventory_surf, vertical, constants):
    """
    Render the Header of the cargo manifest
    :param inventory_surf: Surface to render on
    :param vertical: int y value in pixels to render
    :param constants: constants
    :return: the current int vertical value (one line for the header)
    """
    constants['font'].set_underline(True)
    header_list = ['Qty', 'Weight', 'Volume', 'Total Wt', 'Total Vol']
    horizontal = constants['margin']
    
    inventory_surf.blit(constants['font'].render("Manifest", True, constants['colors']['text']),
                        (horizontal, vertical))
    horizontal += 2 * constants['tab']
    for header in header_list:
        text = constants['font'].render(header, True, constants['colors']['text'])
        text_rect = text.get_rect(topright=(horizontal, vertical))
        inventory_surf.blit(text, text_rect)
        horizontal += constants['tab']
    constants['font'].set_underline(False)
    
    vertical += constants['font'].get_height() + constants['margin']
    return vertical


def render_cargo_totals(inventory_surf, cargo, vertical, constants):
    """
    Render the weight and volume totals at the bottom of the manifest
    :param inventory_surf: Surface to render on
    :param cargo: Cargo component
    :param vertical: int y value in pixels to render
    :param constants: constants
    :return: the current int vertical value
    """
    horizontal = 4 * constants['tab'] + constants['margin']
    text = constants['font'].render('Totals:', True, constants['colors']['text'])
    text_rect = text.get_rect(topright=(horizontal, vertical))
    inventory_surf.blit(text, text_rect)
    
    for field in [cargo.weight, cargo.volume]:
        horizontal += constants['tab']
        render_cargo_info(surface=inventory_surf,
                          field=field,
                          font=constants['font'],
                          color=constants['colors']['text'],
                          horizontal=horizontal,
                          vertical=vertical)
    vertical += constants['font'].get_height() + constants['margin']
    return vertical


def render_cargo(inventory_surf, cargo, vertical, constants):
    """
    Render the name and quantity, the send to subroutine for the float renders of weight and volume
    :param inventory_surf: Surface to render on
    :param cargo: Cargo component
    :param vertical: int y value in pixels to render
    :param constants: constants
    :return: the current int vertical value
    """
    for item in cargo.manifest:
        horizontal = constants['margin']
        inventory_surf.blit(constants['icons'][item.icon], (constants['margin'], vertical))
        
        item_name = constants['font'].render(item.name, True, constants['colors']['text'])
        inventory_surf.blit(item_name, (constants['icons'][item.icon].get_width() + 2 * constants['margin'], vertical))
        horizontal += 2 * constants['tab']
        
        item_qty = constants['font'].render(str(item.quantity), True, constants['colors']['text'])
        text_rect = item_qty.get_rect(topright=(horizontal, vertical))
        inventory_surf.blit(item_qty, text_rect)
        
        for field in [item.weight, item.volume, item.get_item_weight(), item.get_item_volume()]:
            horizontal += constants['tab']
            render_cargo_info(surface=inventory_surf,
                              field=field,
                              font=constants['font'],
                              color=constants['colors']['text'],
                              horizontal=horizontal,
                              vertical=vertical)
        
        vertical += constants['font'].get_height() + constants['margin']
    return vertical


def render_cargo_info(surface, field, font, color, horizontal, vertical):
    """
    Render float weight and volume fields for a type of cargo
    :param surface: Surface to render on
    :param field: id of which field to render (weight, volume)
    :param font: Font used to render
    :param color: tuple of color values
    :param horizontal: int x in pixels for render location
    :param vertical: int y in pixels for render location
    :return: None
    """
    text = font.render("{:10.2f}".format(field), True, color)
    # print(horizontal, vertical)
    text_rect = text.get_rect(topright=(horizontal, vertical))
    surface.blit(text, text_rect)


def render_messages(message_log, constants):
    """
    Render the messages in the message panel - adjusted by view
    :param message_log: the MessageLog with messages to render
    :param constants: constants
    :return: bordered Surface to render on main display
    """
    message_surf = pygame.Surface((constants['message_width'] - 2 * constants['margin'],
                                   constants['message_height'] - 2 * constants['margin']))
    message_surf.fill(constants['colors']['dark_gray'])
    
    y = constants['margin'] // 2
    for message in message_log.messages[message_log.view_pointer:message_log.view_pointer
                                        + constants['message_panel_size']]:
        message_text = constants['font'].render(str(message.text), True, message.color)
        message_surf.blit(message_text, (0, y))
        y += constants['font'].get_height() + constants['margin'] // 2
    
    border_panel = pygame.Surface((constants['message_width'], constants['message_height']))
    
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    border_panel.blit(message_surf, (constants['margin'], constants['margin']))
    return border_panel


def render_board(game_map, player, entities, constants, game_state, game_time, game_weather):
    """
    Generate the surface containing the play area information
    :param game_map: map information
    :param player: player Entity information (mostly for centering camera)
    :param entities: list of Entity objects to render
    :param constants: constants
    :param game_state: rendering switches depending on GameState value
    :param game_time: current time of the game
    :param game_weather: current weather in the map
    :return: bordered Surface to render on main display
    """
    game_map_surf = pygame.Surface((constants['board_width'] * constants['tile_size'] - 2 * constants['margin'],
                                    constants['board_height'] * constants['tile_size'] - constants['half_tile']))
    game_map_surf.fill(constants['colors']['dark_gray'])
    
    if game_state == GameStates.TARGETING:
        targeted_hexes = []
        if game_map.in_bounds(x=player.x, y=player.y, margin=-1) \
                and not (game_map.terrain[player.x][player.y].decoration
                         and game_map.terrain[player.x][player.y].decoration.name == "Port"):
            targeted_hexes = get_hex_neighbors(player.x, player.y)
            targeted_hexes.append((player.x, player.y))
        if game_map.in_bounds(x=player.x, y=player.y, margin=-1):
            if game_map.terrain[player.x][player.y].decoration is None \
                    or (game_map.terrain[player.x][player.y].decoration
                        and game_map.terrain[player.x][player.y].decoration.name != "Port"):
                targeted_hexes.extend(get_target_hexes(player))
    
    for x in range(player.x - 10, player.x + 11):
        for y in range(player.y - 10, player.y + 11):
            if (0 <= x < game_map.width) and (0 <= y < game_map.height) and game_map.terrain[x][y].seen:
                game_map_surf.blit(constants['icons'][game_map.terrain[x][y].icon],
                                   (x * constants['tile_size'] - 2 * constants['margin'],
                                    y * constants['tile_size'] + x % 2 * constants['half_tile']
                                    - constants['half_tile'] - 2 * constants['margin']))
                if game_map.terrain[x][y].decoration:
                    game_map_surf.blit(constants['icons'][game_map.terrain[x][y].decoration.icon],
                                       (x * constants['tile_size'] - constants['margin'],
                                        y * constants['tile_size'] + (x % 2) * constants['half_tile']
                                        - constants['half_tile']))
                
                # TODO: move this here eventually ??
                # if (x, y) not in player.view.fov:
                #     game_map_surf.blit(constants['icons']['shade'],
                #                        (x * constants['tile_size'] - 2 * constants['margin'],
                #                         y * constants['tile_size'] + x % 2 * constants['half_tile']
                #                         - constants['half_tile'] - 2 * constants['margin']))  # -10 for big tile size
                
                if game_state == GameStates.TARGETING:
                    if (x, y) in targeted_hexes and (x, y) in player.view.fov:
                        icon = constants['icons']['highlight']
                        game_map_surf.blit(icon, (x * constants['tile_size'] - 2 * constants['margin'],
                                                  y * constants['tile_size'] + x % 2 * constants['half_tile']
                                                  - constants['half_tile'] - 2 * constants['margin']))
    
    ordered_entities = sorted(entities, key=lambda e: e.render_order.value)
    for entity in ordered_entities:
        if (0 <= entity.x < game_map.width) \
                and (0 <= entity.y < game_map.height) \
                and (entity.x, entity.y) in player.view.fov:
            if entity.icon:
                if entity.mast_sail and not game_state == GameStates.PLAYER_DEAD:
                    icon = create_ship_icon(entity=entity, constants=constants)
                else:
                    icon = constants['icons'][entity.icon]
            else:
                icon = None
            
            if icon and entity.mobile and not game_state == GameStates.PLAYER_DEAD:
                game_map_surf.blit(rot_center(image=icon, angle=direction_angle[entity.mobile.direction]),
                                   (entity.x * constants['tile_size'] - constants['margin'],
                                    entity.y * constants['tile_size'] + entity.x % 2 * constants['half_tile']
                                    - constants['half_tile']))
            elif icon:
                game_map_surf.blit(icon,
                                   (entity.x * constants['tile_size'] - constants['margin'],
                                    entity.y * constants['tile_size'] + entity.x % 2 * constants['half_tile']
                                    - constants['half_tile']))
    
    for x in range(player.x - 10, player.x + 11):
        for y in range(player.y + 10, player.y - 11, -1):
            if (0 <= x < game_map.width) \
                    and (0 <= y < game_map.height) \
                    and game_map.terrain[x][y].seen \
                    and (x, y) not in player.view.fov:
                game_map_surf.blit(constants['icons']['shade'],
                                   (x * constants['tile_size'] - 2 * constants['margin'],
                                    y * constants['tile_size'] + x % 2 * constants['half_tile']
                                    - constants['half_tile'] - 2 * constants['margin']))  # -10 due to larger tile size
            if (0 <= x < game_map.width) \
                    and (0 <= y < game_map.height) \
                    and game_map.terrain[x][y].fog \
                    and (x, y) in player.view.fov:
                game_map_surf.blit(constants['icons']['fog'],
                                   (x * constants['tile_size'] - 2 * constants['margin'],
                                    y * constants['tile_size'] + x % 2 * constants['half_tile']
                                    - constants['half_tile'] - 2 * constants['margin']))
    
    view_surf = pygame.Surface((constants['view_width'] - 2 * constants['margin'],
                                constants['view_height'] - 2 * constants['margin']))
    view_surf.blit(game_map_surf, (constants['view_width'] // 2
                                   - constants['tile_size'] * player.x
                                   - constants['half_tile'],
                                   constants['view_height'] // 2
                                   + constants['half_tile'] * ((player.x + 1) % 2)
                                   - constants['tile_size'] * player.y
                                   - constants['half_tile']
                                   - constants['margin']))
    
    render_time(game_time=game_time, view_surf=view_surf, constants=constants)
    render_weather(game_time=game_time, game_weather=game_weather, view_surf=view_surf, constants=constants)
    render_wind(direction=game_map.wind_direction, view_surf=view_surf, constants=constants)
    
    border_panel = pygame.Surface((constants['view_width'],
                                   constants['view_height']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    border_panel.blit(view_surf, (constants['margin'], constants['margin']))
    return border_panel


def render_wind(direction, view_surf, constants):
    """
    Render the wind information
    :param direction: direction the wind is blowing
    :param view_surf: Surface to render on
    :param constants: constants
    :return: None
    """
    wind_dir = {0: 'North',
                1: 'Northwest',
                2: 'Southwest',
                3: 'South',
                4: 'Southeast',
                5: 'Northeast'}
    if direction is not None:
        text = 'Wind to {}'.format(wind_dir[direction])
    else:
        text = 'No Wind'
    (width, height) = constants['font'].size(text)
    wind_text = constants['font'].render(text, True, constants['colors'].get('text'))
    compass = constants['icons']['compass']
    
    wind_surf = pygame.Surface((width + constants['margin'] + compass.get_width(), compass.get_height()))
    wind_surf.fill(constants['colors']['dark_gray'])
    wind_surf.blit(wind_text, (0, (wind_surf.get_height() - constants['font'].get_height()) // 2 + 1))
    wind_surf.blit(compass, (wind_surf.get_width() - compass.get_width(), 0))
    
    if direction is not None:
        wind_surf.blit(rot_center(image=constants['icons']['pointer'], angle=direction_angle[direction]),
                       (wind_surf.get_width() - compass.get_width(), 0))
    
    border_panel = pygame.Surface((wind_surf.get_width() + 2 * constants['margin'],
                                   wind_surf.get_height() + 2 * constants['margin']))
    border_panel.blit(wind_surf, (constants['margin'], constants['margin']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    view_surf.blit(border_panel, (view_surf.get_width() - border_panel.get_width(), 0))


def render_time(game_time, view_surf, constants):
    """
    Render the time information
    :param game_time: current game Time
    :param view_surf: Surface to render on
    :param constants: constants
    :return: None
    """
    text = '{}.{:02d}.{} {:02d}:{:02d}'.format(game_time.year, game_time.month, game_time.day, game_time.hrs,
                                               game_time.mins)
    (width, height) = constants['font'].size(text)
    time_text = constants['font'].render(text, True, constants['colors'].get('text'))
    time_surf = pygame.Surface((width, height * 2))
    time_surf.fill(constants['colors']['dark_gray'])
    time_surf.blit(time_text, (0, 1))
    text = game_time.get_time_of_day_info['name']
    time_text = constants['font'].render(text, True, constants['colors'].get('text'))
    time_surf.blit(time_text, (0, height + 1))
    
    border_panel = pygame.Surface((width + 2 * constants['margin'],
                                   2 * height + 2 * constants['margin']))
    border_panel.blit(time_surf, (constants['margin'], constants['margin']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    view_surf.blit(border_panel, (0, 0))


def render_weather(game_time, game_weather, view_surf, constants):
    """
    Render the weather information
    :param game_time: current game Time
    :param game_weather: current map Weather
    :param view_surf: Surface to render on
    :param constants: constants
    :return: None
    """
    weather_dict = game_weather.get_weather_info
    time_dict = game_time.get_time_of_day_info
    
    text = '{}'.format(weather_dict['name'].capitalize())
    (width, height) = constants['font'].size(text)
    weather_text = constants['font'].render(text, True, constants['colors'].get('text'))
    
    if 6 <= game_time.hrs < 18:
        icon = constants['icons']['sun']
    else:
        icon = constants['icons']['moon']
    
    numeric_time = 100 * game_time.hrs + 100 * game_time.mins // 60  # Example: 6:45 = 675, 21:30 = 2150
    if numeric_time < 600:
        relative_time = 600 + numeric_time
    elif 600 <= numeric_time < 1800:
        relative_time = numeric_time - 600
    else:  # numeric_time >= 1800:
        relative_time = numeric_time - 1800
    
    icon_x = relative_time * (constants['tile_size'] * 4) // 1200
    
    if relative_time <= 300:
        icon_y = (constants['tile_size']) - icon_x
    elif relative_time >= 900:
        icon_y = icon_x - (constants['tile_size'] * 3)
    else:
        icon_y = 0
    
    # print(numeric_time, relative_time, icon_x, icon_y)
    sky_surf = pygame.Surface((4 * constants['tile_size'], constants['tile_size']))
    sky_surf.fill(constants['colors'][time_dict['sky']])
    sky_surf.blit(icon, (icon_x - 8, icon_y))
    
    if not (600 <= numeric_time < 1800):
        moon_shadow_icon = constants['icons']['moon_shadow']
        moon_shadow_icon = colorize(image=moon_shadow_icon, new_color=constants['colors'][time_dict['sky']])
        
        if numeric_time >= 1800:  # account for day change in middle of night
            offset = 0
        else:
            offset = 1
        sky_surf.blit(moon_shadow_icon, (icon_x - abs(game_time.day - 15 - offset) - 8, icon_y))
    
    icon = constants['icons'][weather_dict['name'].lower()]
    for x in range(sky_surf.get_width() // icon.get_width()):
        sky_surf.blit(icon, (x * icon.get_width(), (x + 1) % 2))
    
    weather_surf = pygame.Surface((width + constants['margin'] + sky_surf.get_width(), constants['tile_size']))
    weather_surf.fill(constants['colors']['dark_gray'])
    weather_surf.blit(weather_text, (0, (constants['tile_size'] - height) // 2 + 1))
    weather_surf.blit(sky_surf, (width + constants['margin'] - 1, 1))
    
    border_panel = pygame.Surface((weather_surf.get_width() + 2 * constants['margin'],
                                   weather_surf.get_height() + 2 * constants['margin']))
    border_panel.blit(weather_surf, (constants['margin'], constants['margin']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    view_surf.blit(border_panel, ((view_surf.get_width() - border_panel.get_width()) // 2, 0))


def colorize(image, new_color):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param new_color: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy()
    
    # zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(new_color[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    
    return image


def render_status(player, constants):
    """
    Render the player status panel
    :param player: the Player Entity
    :param constants: constants
    :return: bordered Player Status panel
    """
    # Status Panel
    status_panel = pygame.Surface((constants['status_width'] - 2 * constants['margin'],
                                   constants['status_height'] - 2 * constants['margin']))
    status_panel.fill(constants['colors']['dark_gray'])
    
    vertical = 0
    
    vertical = render_entity_info(panel=status_panel,
                                  entity=player,
                                  font=constants['font'],
                                  colors=constants['colors'],
                                  margin=constants['margin'],
                                  vertical=vertical)
    
    border_panel = pygame.Surface((constants['status_width'],
                                   constants['status_height']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    border_panel.blit(status_panel, (constants['margin'], constants['margin']))
    return border_panel


def render_control(game_map, player, entities, constants, game_state):
    """
    Render the currently available keys depending on Game State
    :param game_map: GameMap
    :param player: the player Entity
    :param entities: list of Entities in play area
    :param constants: constants
    :param game_state: current GameState
    :return: bordered Surface to render
    """
    control_panel = pygame.Surface((constants['control_width'] - 2 * constants['margin'],
                                    constants['control_height'] - 2 * constants['margin']))
    control_panel.fill(constants['colors']['dark_gray'])
    
    margin = 2
    vertical = 2
    
    if game_state == GameStates.CURRENT_TURN:
        split = 58
        arrow_keys = [{'rotation': 0, 'text': 'Row'},
                      {'rotation': 180, 'text': 'Drag'},
                      {'rotation': 90, 'text': 'Turn Port'},
                      {'rotation': 270, 'text': 'Turn Starboard'}]
        for key in arrow_keys:
            vertical = make_arrow_button(panel=control_panel,
                                         split=split,
                                         margin=margin,
                                         rotation=key['rotation'],
                                         text=key['text'],
                                         icon=constants['icons']['arrow'],
                                         font=constants['font'],
                                         color=constants['colors']['text'],
                                         vertical=vertical)
        text_keys = [{'name': 'Cmd', 'text': 'Targeting'}]
        if player.mast_sail and player.mast_sail.masts:
            text_keys.append({'name': 'Shift', 'text': 'Sails'})
        text_keys.append({'name': 'Opt', 'text': 'Special'})
        spacebar = False
        if game_map.in_bounds(player.x, player.y) \
                and game_map.terrain[player.x][player.y].decoration \
                and game_map.terrain[player.x][player.y].decoration.name == 'Port':
            text_keys.append({'name': 'Space', 'text': 'Visit Town'})
            spacebar = True
        else:
            for entity in entities:
                if (player.x, player.y) == (entity.x, entity.y) \
                        and not entity.ai and not (entity.name == 'player'
                                                   or entity.name == ''):
                    text_keys.append({'name': 'Space', 'text': 'Salvage'})
                    spacebar = True
        if not spacebar:
            text_keys.append({'name': 'Space', 'text': 'Pass'})
        text_keys.append({'name': 'Esc', 'text': 'Quit'})
        for key in text_keys:
            vertical = make_text_button(panel=control_panel,
                                        split=split,
                                        margin=margin,
                                        name=key['name'],
                                        text=key['text'],
                                        font=constants['font'],
                                        color=constants['colors']['text'],
                                        bkg_color=constants['colors']['dark_gray'],
                                        vertical=vertical)
    elif game_state == GameStates.TARGETING:
        split = 58
        arrow_keys = []
        text_keys = []
        if game_map.in_bounds(player.x, player.y, -1) \
                and not (game_map.terrain[player.x][player.y].decoration
                         and game_map.terrain[player.x][player.y].decoration.name == 'Port'):
            if player.weapons.verify_target_at_location('Bow', entities):
                arrow_keys.append({'rotation': 0, 'text': 'Attack Fore'})
            if player.weapons.verify_target_at_location('Stern', entities):
                arrow_keys.append({'rotation': 180, 'text': 'Attack Aft'})
            if player.weapons.verify_target_at_location('Port', entities):
                arrow_keys.append({'rotation': 90, 'text': 'Attack Port'})
            if player.weapons.verify_target_at_location('Starboard', entities):
                arrow_keys.append({'rotation': 270, 'text': 'Attack Starboard'})
            if player.crew.verify_arrow_target(entities):
                text_keys.append({'name': 'Space', 'text': 'Arrow Attack'})
        for key in arrow_keys:
            vertical = make_arrow_button(panel=control_panel,
                                         split=split,
                                         margin=margin,
                                         rotation=key['rotation'],
                                         text=key['text'],
                                         icon=constants['icons']['arrow'],
                                         font=constants['font'],
                                         color=constants['colors']['text'],
                                         vertical=vertical)
        text_keys.append({'name': 'Cmd', 'text': 'Exit Targeting'})
        text_keys.append({'name': 'Esc', 'text': 'Exit Targeting'})
        for key in text_keys:
            vertical = make_text_button(panel=control_panel,
                                        split=split,
                                        margin=margin,
                                        name=key['name'],
                                        text=key['text'],
                                        font=constants['font'],
                                        color=constants['colors']['text'],
                                        bkg_color=constants['colors']['dark_gray'],
                                        vertical=vertical)
    elif game_state == GameStates.SAILS:
        split = 58
        arrow_keys = []
        if player.mast_sail and player.mast_sail.max_sails > 0:
            if player.mast_sail.current_sails < player.mast_sail.max_sails:
                arrow_keys.append({'rotation': 0, 'text': 'Raise Sails'})
            if player.mast_sail.current_sails > 0:
                arrow_keys.append({'rotation': 180, 'text': 'Lower Sails'})
            # left repair sails
            # right repair masts
        for key in arrow_keys:
            vertical = make_arrow_button(panel=control_panel,
                                         split=split,
                                         margin=margin,
                                         rotation=key['rotation'],
                                         text=key['text'],
                                         icon=constants['icons']['arrow'],
                                         font=constants['font'],
                                         color=constants['colors']['text'],
                                         vertical=vertical)
        text_keys = [{'name': 'Shift', 'text': 'Exit Adjust Sails'},
                     {'name': 'Esc', 'text': 'Exit Adjust Sails'}]
        for key in text_keys:
            vertical = make_text_button(panel=control_panel,
                                        split=split,
                                        margin=margin,
                                        name=key['name'],
                                        text=key['text'],
                                        font=constants['font'],
                                        color=constants['colors']['text'],
                                        bkg_color=constants['colors']['dark_gray'],
                                        vertical=vertical)
    elif game_state == GameStates.SPECIAL:
        split = 58
        arrow_keys = [{'rotation': 0, 'text': 'Ram'},
                      {'rotation': 180, 'text': 'Drop Mines'},
                      {'rotation': 90, 'text': 'Assign Crew'},
                      {'rotation': 270, 'text': 'Assign Crew'}]
        for key in arrow_keys:
            vertical = make_arrow_button(panel=control_panel,
                                         split=split,
                                         margin=margin,
                                         rotation=key['rotation'],
                                         text=key['text'],
                                         icon=constants['icons']['arrow'],
                                         font=constants['font'],
                                         color=constants['colors']['text'],
                                         vertical=vertical)
        text_keys = [{'name': 'Space', 'text': 'Cargo'},
                     {'name': 'Opt', 'text': 'Quit'},
                     {'name': 'Esc', 'text': 'Quit'}]
        for key in text_keys:
            vertical = make_text_button(panel=control_panel,
                                        split=split,
                                        margin=margin,
                                        name=key['name'],
                                        text=key['text'],
                                        font=constants['font'],
                                        color=constants['colors']['text'],
                                        bkg_color=constants['colors']['dark_gray'],
                                        vertical=vertical)
    elif game_state == GameStates.CARGO:
        split = 58
        # arrow_keys = [{'rotation': 0, 'text': 'Ram'},
        #               {'rotation': 180, 'text': 'Drop Mines'},
        #               {'rotation': 90, 'text': 'Assign Crew'},
        #               {'rotation': 270, 'text': 'Assign Crew'}]
        # for key in arrow_keys:
        #     vertical = make_arrow_button(panel=control_panel,
        #                                          split=split,
        #                                          margin=margin,
        #                                          rotation=key['rotation'],
        #                                          text=key['text'],
        #                                          icon=constants['icons']['arrow'],
        #                                          font=constants['font'],
        #                                          color=constants['colors']['text'],
        #                                          vertical=vertical)
        text_keys = [{'name': 'Space', 'text': 'Exit Cargo'},
                     {'name': 'Esc', 'text': 'Exit Cargo'}]
        for key in text_keys:
            vertical = make_text_button(panel=control_panel,
                                        split=split,
                                        margin=margin,
                                        name=key['name'],
                                        text=key['text'],
                                        font=constants['font'],
                                        color=constants['colors']['text'],
                                        bkg_color=constants['colors']['dark_gray'],
                                        vertical=vertical)
    else:  # Dead
        split = 58
        text_keys = [{'name': 'Esc', 'text': 'Quit'}]
        for key in text_keys:
            vertical = make_text_button(panel=control_panel,
                                        split=split,
                                        margin=margin,
                                        name=key['name'],
                                        text=key['text'],
                                        font=constants['font'],
                                        color=constants['colors']['text'],
                                        bkg_color=constants['colors']['dark_gray'],
                                        vertical=vertical)
    
    border_panel = pygame.Surface((constants['control_width'],
                                   constants['control_height']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    border_panel.blit(control_panel, (constants['margin'], constants['margin']))
    return border_panel


# def render_mouse_coords(status_panel, constants, grid_x, grid_y):
#     xy_text = constants['font'].render('X: {}, Y: {}'.format(grid_x, grid_y), True, constants['colors'].get('text'))
#     xy_rect = xy_text.get_rect()
#     xy_rect.center = (status_panel.get_width() // 2, xy_text.get_height() * 2)
#     status_panel.blit(xy_text, xy_rect)

def make_arrow_button(panel, split, margin, rotation, text, icon, font, color, vertical):
    """
    Creates and renders an arrow button and description in control panel
    :param panel: Surface to render on
    :param split: vertical line - render button on one side, text on the other
    :param margin: int spacing in pixels
    :param rotation: degrees to rotate icon
    :param text: str action corresponding to the arrow button
    :param icon: arrow icon
    :param font: Font for rendering name
    :param color: color of the text to render
    :param vertical: int y value to render at
    :return: current vertical value
    """
    panel.blit(rot_center(image=icon, angle=rotation),
               (split - margin - icon.get_width(), vertical))
    panel.blit(font.render(text, True, color),
               (split + margin, vertical + 1))
    vertical += font.get_height() + margin
    return vertical


def make_text_button(panel, split, margin, name, text, font, color, bkg_color, vertical):
    """
    Creates and renders the key button and description in control panel
    :param panel: Surface to render on
    :param split: vertical line - render button on one side, text on the other
    :param margin: int spacing in pixels
    :param name: str name of the key
    :param text: str action corresponding to the text button
    :param font: Font for rendering name and key
    :param color: color of the text to render
    :param bkg_color: background color (for reversing the colors of the key name)
    :param vertical: int y value to render at
    :return: current vertical value
    """
    key_text = font.render(name, True, bkg_color)
    w, h = font.size(name)
    key_surf = pygame.Surface((w + 3, h))
    key_surf.fill(color)
    key_surf.blit(key_text, (1, 1))
    panel.blit(key_surf, (split - margin - key_surf.get_width(), vertical))
    panel.blit(font.render(text, True, color),
               (split + margin, vertical + 1))
    vertical += font.get_height() + margin
    return vertical


def render_border(panel, color):
    """
    Draws a border around the edge of the given panel
    :param panel: Surface to draw on
    :param color: color of the border
    :return: None
    """
    pygame.draw.lines(panel, color, True,
                      ((2, 2),
                       (panel.get_width() - 3, 2),
                       (panel.get_width() - 3, panel.get_height() - 3),
                       (2, panel.get_height() - 3)), 1)


def render_entity_info(panel, entity, font, colors, margin, vertical):
    """
    Renders entity information on a given panel
    :param panel: Surface to draw on
    :param entity: list of Entity Objects
    :param font: Font for rendering
    :param colors: dict of color values
    :param margin: int pixel spacing
    :param vertical: int y position for rendering
    :return: int current vertical value
    """
    # ship name
    name_text = font.render(entity.name, True, colors['text'])
    panel.blit(name_text, (0, vertical + 1))
    if entity.name == 'player':
        text = 'X:{} Y:{}'.format(entity.x, entity.y)
        coords_text = font.render(text, True, colors['text'])
        (width, height) = font.size(text)
        panel.blit(coords_text, (panel.get_width() - width, vertical + 1))
    vertical += font.get_height() + margin // 2
    if entity.mast_sail and entity.mast_sail.masts > 0:
        panel.blit(make_bar(text='Sails', font=font,
                            font_color=colors['text'],
                            current=entity.mast_sail.current_sails,
                            maximum=entity.mast_sail.max_sails,
                            top_color=colors['light_blue'],
                            bottom_color=colors['dark_blue'],
                            bar_width=panel.get_width()),
                   (0, vertical))
        vertical += font.get_height() + 1
        panel.blit(make_bar(text='Sails HPs', font=font,
                            font_color=colors['text'],
                            current=entity.mast_sail.sail_hp,
                            maximum=entity.mast_sail.sail_hp_max,
                            top_color=colors['light_red'],
                            bottom_color=colors['dark_red'],
                            bar_width=panel.get_width()),
                   (0, vertical))
        vertical += font.get_height() + margin // 2
        panel.blit(make_bar(text='Masts HPs', font=font,
                            font_color=colors['text'],
                            current=entity.mast_sail.mast_hp,
                            maximum=entity.mast_sail.mast_hp_max,
                            top_color=colors['light_red'],
                            bottom_color=colors['dark_red'],
                            bar_width=panel.get_width()),
                   (0, vertical))
        vertical += font.get_height() + margin // 2
    if entity.mobile:
        panel.blit(make_bar(text='Momentum', font=font,
                            font_color=colors['text'],
                            current=entity.mobile.current_momentum,
                            maximum=entity.mobile.max_momentum,
                            top_color=colors['light_green'],
                            bottom_color=colors['dark_green'],
                            bar_width=panel.get_width()),
                   (0, vertical))
        vertical += font.get_height() + margin // 2
        panel.blit(make_bar(text='Speed', font=font,
                            font_color=colors['text'],
                            current=entity.mobile.current_speed,
                            maximum=entity.mobile.max_speed,
                            top_color=colors['light_green'],
                            bottom_color=colors['dark_green'],
                            bar_width=panel.get_width()),
                   (0, vertical))
        vertical += font.get_height() + margin // 2
    if entity.fighter:
        panel.blit(make_bar(text='{} Points'.format(entity.fighter.name.capitalize()), font=font,
                            font_color=colors['text'],
                            current=entity.fighter.hps,
                            maximum=entity.fighter.max_hps,
                            top_color=colors['light_red'],
                            bottom_color=colors['dark_red'],
                            bar_width=panel.get_width()),
                   (0, vertical))
        vertical += font.get_height() + margin // 2
    if entity.crew:
        panel.blit(make_bar(text='Crew'.format(entity.fighter.name.capitalize()), font=font,
                            font_color=colors['text'],
                            current=len(entity.crew.crew_list),
                            maximum=entity.crew.max_crew,
                            top_color=colors['light_red'],
                            bottom_color=colors['dark_red'],
                            bar_width=panel.get_width()),
                   (0, vertical))
        vertical += font.get_height() + margin // 2
    
    if entity.weapons:
        vertical = render_weapons(panel=panel,
                                  entity=entity,
                                  font=font,
                                  colors=colors,
                                  vertical=vertical)
    
    return vertical


def render_weapons(panel, entity, font, colors, vertical):
    """
    Render the Weapons of an entity - name, location, current cooldown, and HPs
    :param panel: Surface to draw on
    :param entity: list of Entity Objects
    :param font: Font for rendering
    :param colors: dict of color values
    :param vertical: int y position for rendering
    :return: int current vertical value
    """
    for weapon in entity.weapons.weapon_list:
        if weapon.current_cd == 0:
            color = colors['text']
        else:
            color = colors['gray']
        weapon_text = font.render("{} {}".format(weapon.location, weapon.name), True, color)
        panel.blit(weapon_text, (0, vertical))
        hp_text = font.render("[{}] {}/{}".format(weapon.current_cd, weapon.hps, weapon.max_hps), True, color)
        panel.blit(hp_text, (panel.get_width() - hp_text.get_width(), vertical))
        vertical += font.get_height()
    return vertical


def make_bar(text, font, font_color, current, maximum, top_color, bottom_color, bar_width):
    """
    Renders a visual meter
    :param text: name of the values to render
    :param font: Font for rendering
    :param font_color: text color to render
    :param current: current value
    :param maximum: maximum value
    :param top_color: brighter top color of bar
    :param bottom_color: darker background color of bar
    :param bar_width: width of the bar surface
    :return: Surface to render
    """
    max_bar = pygame.Surface((bar_width, font.get_height()))
    max_bar.fill(bottom_color)
    if maximum > 0:
        current_bar_length = math.floor(float(current / maximum * bar_width))
        if current_bar_length < 0:
            current_bar_length = 0
        current_bar = pygame.Surface((current_bar_length, font.get_height()))
        current_bar.fill(top_color)
        max_bar.blit(current_bar, (0, 0))
    bar_text = font.render('{}:'.format(text), True, font_color)
    bar_nums = font.render('{}/{}'.format(current, maximum), True, font_color)
    max_bar.blit(bar_text, (1, 1))
    max_bar.blit(bar_nums, (max_bar.get_width() - bar_nums.get_width(), 1))
    
    return max_bar


def rot_center(image, angle):
    """
    Rotate an image while keeping its center and size - counter clockwise rotation
    :param image: Surface icon
    :param angle: how much to rotate image
    :return: rotated icon as a Surface
    
    """
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def render_map(game_map, player, entities, constants):
    """
    Render the current play area
    :param game_map: the current GameMap
    :param player: player Entity
    :param entities: list of Entity objects
    :param constants: constants
    :return: bordered panel to render
    """
    map_surf = pygame.Surface((constants['map_width'] - 2 * constants['margin'],
                               constants['map_height'] - 2 * constants['margin']))
    map_surf.fill(constants['colors']['dark_gray'])
    port = None
    block = pygame.Surface(constants['map_block'])
    small_block = pygame.Surface((constants['block_size'] // 2, constants['block_size'] // 2))
    big_block = pygame.Surface((constants['block_size'] + 2, constants['block_size'] + 2))
    for x in range(constants['board_width']):
        for y in range(constants['board_height']):
            if game_map.terrain[x][y].seen:
                block.fill(constants['colors'][game_map.terrain[x][y].color])
                map_surf.blit(block, (x * constants['block_size'],
                                      y * constants['block_size'] + (x % 2) * (constants['block_size'] // 2)
                                      - constants['block_size'] // 2))
                if game_map.terrain[x][y].decoration:
                    if game_map.terrain[x][y].decoration.name == 'Port':
                        port = (x, y)
                    else:
                        small_block.fill(constants['colors'][game_map.terrain[x][y].decoration.color])
                        map_surf.blit(small_block, (x * constants['block_size']
                                                    + 1,
                                                    y * constants['block_size']
                                                    + (x % 2) * (constants['block_size'] // 2)
                                                    - constants['block_size'] // 2
                                                    + 1))
    if port:
        (x, y) = port
        big_block.fill(constants['colors'][game_map.terrain[x][y].decoration.color])
        map_surf.blit(big_block, (x * constants['block_size']
                                  - 1,
                                  y * constants['block_size']
                                  + (x % 2) * (constants['block_size'] // 2)
                                  - constants['block_size'] // 2
                                  - 1))
        block.fill(constants['colors']['black'])
        map_surf.blit(block, (x * constants['block_size'],
                              y * constants['block_size']
                              + (x % 2) * (constants['block_size'] // 2)
                              - constants['block_size'] // 2))
    
    for entity in entities:
        if (0 <= entity.x < game_map.width) and (0 <= entity.y < game_map.height) \
                and (entity.x, entity.y) in player.view.fov \
                and entity.icon:
            if entity.name == "player":
                block.fill(constants['colors']['white'])
            else:
                block.fill(constants['colors']['light_red'])
            map_surf.blit(block, (entity.x * constants['block_size'],
                                  entity.y * constants['block_size']
                                  + (entity.x % 2) * (constants['block_size'] // 2)
                                  - constants['block_size'] // 2))
    
    border_panel = pygame.Surface((constants['map_width'],
                                   constants['map_height']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    border_panel.blit(map_surf, (constants['margin'], constants['margin']))
    
    return border_panel


def get_info_under_mouse(game_map, player, entities, mouse_x, mouse_y, constants):
    """
    Returns a surface of information under mouse location, including terrain, decorations, entity information
    :param game_map: current GameMap
    :param player: player Entity
    :param entities: list of Entity Objects
    :param mouse_x: int x value of mouse location in pixels
    :param mouse_y: int y value of mouse location in pixels
    :param constants: constants
    :return: bordered Surface of information under mouse location
    """
    grid_x, grid_y = get_grid_from_coords(coords=(mouse_x, mouse_y),
                                          player_coords=(player.x, player.y),
                                          constants=constants)
    vertical = 0
    width = 0
    entity_surf = None
    info_surf = None
    terrain_surf = None
    decor_surf = None
    fog_surf = None
    location_surf = None
    if (0 <= grid_x < game_map.width) \
            and (0 <= grid_y < game_map.height) \
            and game_map.terrain[grid_x][grid_y].seen \
            and constants['map_width'] <= mouse_x < constants['display_width'] - 1 \
            and 0 <= mouse_y <= constants['view_height']:
        
        if game_map.terrain[grid_x][grid_y].elevation >= Elevation.DEEPS:
            location_name = "X:{} Y:{}".format(grid_x, grid_y)
            location_text = constants['font'].render(location_name, True, constants['colors']['text'])
            w, h = constants['font'].size(location_name)
            if width < w:
                width = w
            vertical += h
            location_surf = pygame.Surface((w, h))
            location_surf.fill(constants['colors']['dark_gray'])
            location_surf.blit(location_text, (0, 0))
            
            terrain_name = game_map.terrain[grid_x][grid_y].name
            terrain_text = constants['font'].render(terrain_name, True, constants['colors']['text'])
            w, h = constants['font'].size(terrain_name)
            if w > width:
                width = w
            vertical += h
            terrain_surf = pygame.Surface((w, h))
            terrain_surf.fill(constants['colors']['dark_gray'])
            terrain_surf.blit(terrain_text, (0, 0))
            
            if game_map.terrain[grid_x][grid_y].decoration:
                decor_name = game_map.terrain[grid_x][grid_y].decoration.name
                decor_text = constants['font'].render(decor_name, True, constants['colors']['text'])
                w, h = constants['font'].size(decor_name)
                if w > width:
                    width = w
                vertical += h
                decor_surf = pygame.Surface((w, h))
                decor_surf.fill(constants['colors']['dark_gray'])
                decor_surf.blit(decor_text, (0, 0))
            
            if game_map.terrain[grid_x][grid_y].fog and (grid_x, grid_y) in player.view.fov:
                fog_name = 'Fog'
                fog_text = constants['font'].render('Fog', True, constants['colors']['text'])
                w, h = constants['font'].size(fog_name)
                if w > width:
                    width = w
                vertical += h
                fog_surf = pygame.Surface((w, h))
                fog_surf.fill(constants['colors']['dark_gray'])
                fog_surf.blit(fog_text, (0, 0))
        
        entities_under_mouse = []
        for entity in entities:
            if entity.name != 'player' \
                    and (0 <= entity.x < game_map.width) \
                    and (0 <= entity.y < game_map.height) \
                    and (entity.x, entity.y) in player.view.fov \
                    and (entity.x, entity.y) == (grid_x, grid_y) \
                    and entity.icon:
                entities_under_mouse.append(entity)
        if len(entities_under_mouse) > 0:
            height = 2
            for entity in entities_under_mouse:
                w, h = constants['font'].size(entity.name)
                height += h + constants['margin'] // 2
                if w > width:
                    width = w
                if entity.mobile:
                    w, h = constants['font'].size('Momentum:  {}/{}'.format(entity.mobile.current_momentum,
                                                                            entity.mobile.max_momentum))
                    height += h + constants['margin'] // 2
                    if w > width:
                        width = w
                if entity.mobile:
                    w, h = constants['font'].size('Speed:  {}/{}'.format(entity.mobile.current_speed,
                                                                         entity.mobile.max_speed))
                    height += h + constants['margin'] // 2
                    if w > width:
                        width = w
                if entity.fighter:
                    w, h = constants['font'].size('{} points:  {}/{}'.format(entity.fighter.name.capitalize(),
                                                                             entity.fighter.hps,
                                                                             entity.fighter.max_hps))
                    height += h + constants['margin'] // 2
                    if w > width:
                        width = w
            
            entity_surf = pygame.Surface((width, height + constants['margin'] * (len(entities_under_mouse) - 1)))
            entity_surf.fill(constants['colors']['dark_gray'])
            vert = constants['margin']
            for entity in entities_under_mouse:
                vert += render_entity_info(panel=entity_surf,
                                           entity=entity,
                                           font=constants['font'],
                                           colors=constants['colors'],
                                           margin=constants['margin'],
                                           vertical=vert)
            vertical += entity_surf.get_height()
    
    if location_surf:
        vert = constants['margin']
        info_surf = pygame.Surface((width + 2 * constants['margin'],
                                    vertical + 2 * constants['margin']))
        info_surf.fill(constants['colors']['dark_gray'])
        
        info_surf.blit(location_surf, (constants['margin'], vert))
        vert += constants['font'].get_height()
        if terrain_surf:
            info_surf.blit(terrain_surf, (constants['margin'], vert))
            vert += constants['font'].get_height()
        if decor_surf:
            info_surf.blit(decor_surf, (constants['margin'], vert))
            vert += constants['font'].get_height()
        if fog_surf:
            info_surf.blit(fog_surf, (constants['margin'], vert))
            vert += constants['font'].get_height()
        if entity_surf:
            info_surf.blit(entity_surf, (constants['margin'], vert))
    
    if info_surf:
        render_border(panel=info_surf, color=constants['colors']['text'])
    return info_surf


def create_ship_icon(entity, constants):
    """
    Create ship icon from a spritesheet
    TODO: actually use the ship entity's icon, rather than just counting the size/masts
    :param entity: Entity's icon to be generated
    :param constants: constants
    :return: created ship icon
    """
    size = constants['tile_size']
    icon = pygame.Surface((size, size))
    icon.set_colorkey(constants['colors']['black'])
    name = 'ship_' + str(entity.size.value) + '_mast'
    sheet = constants['icons'][name]
    if entity.mobile.current_speed > 0:
        icon.blit(sheet.subsurface(0, 0, size, size), (0, 0))  # wake
    icon.blit(sheet.subsurface(0, size, size, size), (0, 0))  # hull
    sprite_col = [1]  # masts
    sprite_row = []
    for x in range(0, entity.mast_sail.masts):
        sprite_row.append(x)
    for row in sprite_row:
        # if mast destroyed, skip this row, else
        for col in sprite_col:
            icon.blit(sheet.subsurface(size * col, size * row, size, size), (0, 0))
    sprite_col = [2]  # sails
    sprite_row = []
    for x in range(0, entity.mast_sail.current_sails):
        sprite_row.append(x)
    for row in sprite_row:
        # if sail destroyed, skip this row, else
        # if no emblem: sprite_col = [2]
        # else
        # adjust emblem color
        sprite_col.append(3)  # emblems
        for col in sprite_col:
            icon.blit(sheet.subsurface(size * col, size * row, size, size), (0, 0))
    return icon


def render_main_menu(display, constants, error=None):
    display.fill(constants['colors']['black'])
    
    border_panel = pygame.Surface((constants['display_width'], constants['display_height']))
    render_border(panel=border_panel, color=constants['colors']['text'])
    
    menu_surf = pygame.Surface((constants['display_width'] - 2 * constants['margin'],
                                constants['display_height'] - 2 * constants['margin']))
    menu_surf.fill(constants['colors']['dark_gray'])
    
    vertical = constants['display_width'] // 2
    split = constants['display_height'] // 2
    arrow_keys = [{'rotation': 90, 'text': 'New Game'},
                  {'rotation': 270, 'text': 'Load Saved Game'}]
    for key in arrow_keys:
        vertical = make_arrow_button(panel=menu_surf,
                                     split=split,
                                     margin=constants['margin'],
                                     rotation=key['rotation'],
                                     text=key['text'],
                                     icon=constants['icons']['arrow'],
                                     font=constants['font'],
                                     color=constants['colors']['text'],
                                     vertical=vertical)
    text_keys = [{'name': 'Esc', 'text': 'Exit Game'}]
    for key in text_keys:
        vertical = make_text_button(panel=menu_surf,
                                    split=split,
                                    margin=constants['margin'],
                                    name=key['name'],
                                    text=key['text'],
                                    font=constants['font'],
                                    color=constants['colors']['text'],
                                    bkg_color=constants['colors']['dark_gray'],
                                    vertical=vertical)
    if error:
        error_text = constants['font'].render('No Save Game to Load!', True, constants['colors']['text'])
        menu_surf.blit(error_text, (0, 0))
    border_panel.blit(menu_surf, (constants['margin'], constants['margin']))
    display.blit(border_panel, (0, 0))
    pygame.display.update()
