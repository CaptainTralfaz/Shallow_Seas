import math
from enum import Enum

import pygame

from src.game_states import GameStates
from src.map_objects.map_utils import direction_angle, get_grid_from_coords, get_target_hexes
from src.map_objects.tile import Elevation


class RenderOrder(Enum):
    TERRAIN = 0
    DECORATION = 1
    CORPSE = 2
    FLOATING = 3
    SWIMMING = 4
    PLAYER = 5
    FLYING = 6
    FOG = 7


def render_display(display, game_map, player, entities, constants, mouse_x, mouse_y, message_log, game_state):
    display.fill(constants['colors']['black'])
    
    board_surf = render_board(game_map, player, entities, constants, game_state)
    display.blit(board_surf, (constants['map_width'], 0))
    
    # draw and blit mini-map
    map_surf = render_map(game_map, player, entities, constants)
    display.blit(map_surf, (0, 0))
    
    # draw and blit status panel
    status_surf = render_status(game_map, player, entities, constants, mouse_x, mouse_y, game_state)
    display.blit(status_surf, (0, constants['map_height']))
    
    control_surf = render_control(game_map, player, entities, constants, game_state)
    display.blit(control_surf, (0, constants['map_height'] + constants['status_height']))
    
    message_surf = render_messages(message_log, constants)
    display.blit(message_surf, (constants['status_width'], constants['view_height']))
    
    info_surf = get_info_under_mouse(game_map, player, entities, mouse_x, mouse_y, constants)
    if info_surf:
        location_x = mouse_x + constants['half_tile']
        location_y = mouse_y + constants['half_tile']
        if location_x + info_surf.get_width() > constants['display_width'] - constants['margin']:
            location_x = constants['display_width'] - constants['margin'] - info_surf.get_width()
        if location_y + info_surf.get_height() > constants['view_height'] - constants['margin']:
            location_y = constants['view_height'] - constants['margin'] - info_surf.get_height()
        display.blit(info_surf, (location_x, location_y))
    
    pygame.display.update()


def render_messages(message_log, constants):
    message_surf = pygame.Surface((constants['message_width'] - 2 * constants['margin'],
                                   constants['message_height'] - 2 * constants['margin']))
    message_surf.fill(constants['colors']['dark_gray'])
    
    y = message_surf.get_height() - constants['font'].get_linesize() * (len(message_log.messages) + 1)
    for message in message_log.messages:
        y += constants['font'].get_linesize()
        message_text = constants['font'].render(str(message.text), 1, message.color)
        message_surf.blit(message_text, (0, y))
    
    border_panel = pygame.Surface((constants['message_width'], constants['message_height']))
    
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(message_surf, (constants['margin'], constants['margin']))
    return border_panel


def render_board(game_map, player, entities, constants, game_state):
    game_map_surf = pygame.Surface((constants['board_width'] * constants['tile_size'] - 2 * constants['margin'],
                                    constants['board_height'] * constants['tile_size'] - constants['half_tile']))
    game_map_surf.fill(constants['colors']['dark_gray'])
    
    if game_state == GameStates.TARGETING:
        targeted_hexes = []
        if game_map.in_bounds(player.x, player.y, -1):
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
            if entity.mast_sail and not game_state == GameStates.PLAYER_DEAD:
                icon = create_ship_icon(entity, constants)
            else:
                icon = entity.icon
            
            if icon and entity.mobile and not game_state == GameStates.PLAYER_DEAD:
                game_map_surf.blit(rot_center(icon, direction_angle[entity.mobile.direction]),
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
    
    border_panel = pygame.Surface((constants['view_width'],
                                   constants['view_height']))
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(view_surf, (constants['margin'], constants['margin']))
    return border_panel


def render_status(game_map, player, entities, constants, mouse_x, mouse_y, state):
    # Status Panel
    status_panel = pygame.Surface((constants['status_width'] - 2 * constants['margin'],
                                   constants['status_height'] - 2 * constants['margin']))
    status_panel.fill(constants['colors']['dark_gray'])
    
    # wind direction
    direction_text = constants['font'].render('Wind Direction:', 1, constants['colors'].get('text'))
    status_panel.blit(direction_text, (constants['half_tile'], constants['half_tile']))
    status_panel.blit(constants['icons']['compass'],
                      (constants['status_width'] - 2 * constants['tile_size'] + constants['margin'],
                       2 * constants['margin']))
    if game_map.wind_direction is not None:
        status_panel.blit(rot_center(constants['icons']['pointer'], direction_angle[game_map.wind_direction]),
                          (constants['status_width'] - 2 * constants['tile_size'] + constants['margin'],
                           2 * constants['margin']))
    vertical = constants['tile_size'] + constants['margin']
    
    vertical = render_entity_info(status_panel, player, constants, vertical)
    
    border_panel = pygame.Surface((constants['status_width'],
                                   constants['status_height']))
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(status_panel, (constants['margin'], constants['margin']))
    return border_panel


def render_control(game_map, player, entities, constants, game_state):
    control_panel = pygame.Surface((constants['control_width'] - 2 * constants['margin'],
                                    constants['control_height'] - 2 * constants['margin']))
    control_panel.fill(constants['colors']['dark_gray'])
    
    margin = 3
    vertical = 1
    
    if game_state == GameStates.CURRENT_TURN:
        split = 58
        arrow_keys = [{'rotation': 0, 'text': 'Row'},
                      {'rotation': 180, 'text': 'Drag'},
                      {'rotation': 90, 'text': 'Rotate Port'},
                      {'rotation': 270, 'text': 'Rotate Starboard'}]
        for key in arrow_keys:
            vertical = make_arrow_button(control_panel, split, margin, key['rotation'],
                                         key['text'], constants, vertical)
        text_keys = [{'name': 'Ctrl', 'text': 'Targeting'}]
        if player.mast_sail and player.mast_sail.masts:
            text_keys.append({'name': 'Shift', 'text': 'Sails'})
        text_keys.append({'name': 'Alt', 'text': 'Special'})
        spacebar = False
        if game_map.in_bounds(player.x, player.y) \
                and game_map.terrain[player.x][player.y].decoration \
                and game_map.terrain[player.x][player.y].decoration.name == 'Port':
            text_keys.append({'name': 'Space', 'text': 'Visit Town'})
            spacebar = True
        else:
            for entity in entities:
                if (player.x, player.y) == (entity.x, entity.y) \
                        and not entity.ai and entity.name not in ['player', '']:
                    text_keys.append({'name': 'Space', 'text': 'Salvage'})
                    spacebar = True
        if not spacebar:
            text_keys.append({'name': 'Space', 'text': 'Pass'})
        text_keys.append({'name': 'Esc', 'text': 'Quit'})
        for key in text_keys:
            vertical = make_text_button(control_panel, split, margin, key['name'],
                                        key['text'], constants, vertical)
    elif game_state == GameStates.TARGETING:
        split = 58
        arrow_keys = []
        if player.weapons.verify_target_at_location('Bow', entities):
            arrow_keys.append({'rotation': 0, 'text': 'Attack Fore'})
        if player.weapons.verify_target_at_location('Stern', entities):
            arrow_keys.append({'rotation': 180, 'text': 'Attack Aft'})
        if player.weapons.verify_target_at_location('Port', entities):
            arrow_keys.append({'rotation': 90, 'text': 'Attack Port'})
        if player.weapons.verify_target_at_location('Starboard', entities):
            arrow_keys.append({'rotation': 270, 'text': 'Attack Starboard'})
        for key in arrow_keys:
            vertical = make_arrow_button(control_panel, split, margin, key['rotation'],
                                         key['text'], constants, vertical)
        text_keys = [#{'name': 'Space', 'text': 'Arrow Attack'},
                     {'name': 'Ctrl', 'text': 'Exit Targeting'},
                     {'name': 'Esc', 'text': 'Exit Targeting'}]
        for key in text_keys:
            vertical = make_text_button(control_panel, split, margin, key['name'],
                                        key['text'], constants, vertical)
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
            vertical = make_arrow_button(control_panel, split, margin, key['rotation'],
                                         key['text'], constants, vertical)
        text_keys = [{'name': 'Shift', 'text': 'Exit Adjust Sails'},
                     {'name': 'Esc', 'text': 'Exit Adjust Sails'}]
        for key in text_keys:
            vertical = make_text_button(control_panel, split, margin, key['name'],
                                        key['text'], constants, vertical)

    else:
        split = 58
        text_keys = [{'name': 'Esc', 'text': 'Quit'}]
        for key in text_keys:
            vertical = make_text_button(control_panel, split, margin, key['name'],
                                        key['text'], constants, vertical)
    
    border_panel = pygame.Surface((constants['control_width'],
                                   constants['control_height']))
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(control_panel, (constants['margin'], constants['margin']))
    return border_panel


# def render_mouse_coords(status_panel, constants, grid_x, grid_y):
#     xy_text = constants['font'].render('X: {}, Y: {}'.format(grid_x, grid_y), 1, constants['colors'].get('text'))
#     xy_rect = xy_text.get_rect()
#     xy_rect.center = (status_panel.get_width() // 2, xy_text.get_height() * 2)
#     status_panel.blit(xy_text, xy_rect)

def make_arrow_button(panel, split, margin, rotation, text, constants, vertical):
    panel.blit(rot_center(constants['icons']['arrow'], rotation),
               (split - margin - constants['icons']['arrow'].get_width(), vertical))
    panel.blit(constants['font'].render(text, 1, constants['colors']['text']),
               (split + margin, vertical + 1))
    vertical += constants['font'].get_height() + margin
    return vertical


def make_text_button(panel, split, margin, name, text, constants, vertical):
    key_text = constants['font'].render(name, 1, constants['colors']['dark_gray'])
    w, h = constants['font'].size(name)
    key_surf = pygame.Surface((w + 3, h))
    key_surf.fill(constants['colors']['text'])
    key_surf.blit(key_text, (1, 1))
    panel.blit(key_surf, (split - margin - key_surf.get_width(), vertical))
    panel.blit(constants['font'].render(text, 1, constants['colors']['text']),
               (split + margin, vertical + 1))
    vertical += constants['font'].get_height() + margin
    return vertical


def render_border(panel, color):
    pygame.draw.lines(panel, color, True,
                      ((2, 2),
                       (panel.get_width() - 3, 2),
                       (panel.get_width() - 3, panel.get_height() - 3),
                       (2, panel.get_height() - 3)), 1)


def render_entity_info(panel, entity, constants, vertical):
    font = constants['font']
    # ship name
    name_text = font.render(entity.name, 1, constants['colors']['text'])
    panel.blit(name_text, (0, vertical + 1))
    vertical += font.get_height()
    
    if entity.mast_sail and entity.mast_sail.masts > 0:
        panel.blit(make_bar('Sails', font, constants['colors']['text'],
                            entity.mast_sail.current_sails, entity.mast_sail.max_sails,
                            constants['colors']['light_blue'], constants['colors']['dark_blue'],
                            panel.get_width()), (0, vertical))
        vertical += font.get_height() + constants['margin'] // 2
    if entity.mobile:
        panel.blit(make_bar('Momentum', font, constants['colors']['text'],
                            entity.mobile.current_momentum, entity.mobile.max_momentum,
                            constants['colors']['light_green'], constants['colors']['dark_green'],
                            panel.get_width()), (0, vertical))
        vertical += font.get_height() + constants['margin'] // 2
        panel.blit(make_bar('Speed', font, constants['colors']['text'],
                            entity.mobile.current_speed, entity.mobile.max_speed,
                            constants['colors']['light_green'], constants['colors']['dark_green'],
                            panel.get_width()), (0, vertical))
        vertical += font.get_height() + constants['margin'] // 2
    if entity.fighter:
        panel.blit(make_bar('{} Points'.format(entity.fighter.name.capitalize()), font,
                            constants['colors']['text'],
                            entity.fighter.hps, entity.fighter.max_hps,
                            constants['colors']['light_red'], constants['colors']['dark_red'],
                            panel.get_width()), (0, vertical))
        vertical += font.get_height() + constants['margin'] // 2
    if entity.weapons:
        vertical = render_weapons(panel, entity, constants, vertical)
    
    return vertical


def render_weapons(panel, entity, constants, vertical):
    for weapon in entity.weapons.weapon_list:
        if weapon.current_cd == 0:
            color = constants['colors']['text']
        else:
            color = constants['colors']['gray']
        weapon_text = constants['font'].render("{} {}".format(weapon.location,
                                                              weapon.name), 1, color)
        panel.blit(weapon_text, (0, vertical))
        hp_text = constants['font'].render("[{}]   {}/{}".format(weapon.current_cd,
                                                                 weapon.hps,
                                                                 weapon.max_hps), 1, color)
        panel.blit(hp_text, (panel.get_width() - hp_text.get_width(), vertical))
        vertical += constants['font'].get_height()
    return vertical


def make_bar(text, font, font_color, current, maximum, top_color, bottom_color, bar_width):
    max_bar = pygame.Surface((bar_width, font.get_height()))
    max_bar.fill(bottom_color)
    current_bar_length = math.floor(float(current / maximum * bar_width))
    if current_bar_length < 0:
        current_bar_length = 0
    current_bar = pygame.Surface((current_bar_length, font.get_height()))
    current_bar.fill(top_color)
    bar_text = font.render('{}:'.format(text), 1, font_color)
    bar_nums = font.render('{}/{}'.format(current, maximum), 1, font_color)
    max_bar.blit(current_bar, (0, 0))
    max_bar.blit(bar_text, (1, 1))
    max_bar.blit(bar_nums, (max_bar.get_width() - bar_nums.get_width(), 1))
    
    return max_bar


def clear_all(surface):
    surface.fill((0, 0, 0))


def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image


def render_map(game_map, player, entities, constants):
    map_surf = pygame.Surface((constants['map_width'] - 2 * constants['margin'],
                               constants['map_height'] - 2 * constants['margin']))
    map_surf.fill(constants['colors']['dark_gray'])
    
    block = pygame.Surface(constants['map_block'])
    small_block = pygame.Surface((constants['block_size'] // 2, constants['block_size'] // 2))
    for x in range(constants['board_width']):
        for y in range(constants['board_height']):
            if game_map.terrain[x][y].seen:
                block.fill(constants['colors'][game_map.terrain[x][y].color])
                map_surf.blit(block, (x * constants['block_size'],
                                      y * constants['block_size'] + (x % 2) * (constants['block_size'] // 2)
                                      - constants['block_size'] // 2))
                if game_map.terrain[x][y].decoration:
                    if game_map.terrain[x][y].decoration.name == 'Port':
                        block.fill(constants['colors'][game_map.terrain[x][y].decoration.color])
                        map_surf.blit(block, (x * constants['block_size'],
                                              y * constants['block_size'] + (x % 2) * (constants['block_size'] // 2)
                                              - constants['block_size'] // 2))
                    else:
                        small_block.fill(constants['colors'][game_map.terrain[x][y].decoration.color])
                        map_surf.blit(small_block, (x * constants['block_size'] + 1,
                                                    y * constants['block_size'] + (x % 2) * (
                                                            constants['block_size'] // 2)
                                                    + 1 - constants['block_size'] // 2))
    
    for entity in entities:
        if (0 <= entity.x < game_map.width) and (0 <= entity.y < game_map.height) \
                and (entity.x, entity.y) in player.view.fov \
                and entity.icon:
            if entity.name == "player":
                block.fill(constants['colors']['white'])
            else:
                block.fill(constants['colors']['light_red'])
            map_surf.blit(block, (entity.x * constants['block_size'],
                                  entity.y * constants['block_size'] + (entity.x % 2) * (constants['block_size'] // 2)
                                  - constants['block_size'] // 2))
    
    border_panel = pygame.Surface((constants['map_width'],
                                   constants['map_height']))
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(map_surf, (constants['margin'], constants['margin']))
    
    return border_panel


def get_info_under_mouse(game_map, player, entities, mouse_x, mouse_y, constants):
    grid_x, grid_y = get_grid_from_coords((mouse_x, mouse_y), (player.x, player.y), constants)
    vertical = 0
    width = 0
    entity_surf = None
    info_surf = None
    terrain_surf = None
    decor_surf = None
    location_surf = None
    if (0 <= grid_x < game_map.width) \
            and (0 <= grid_y < game_map.height) \
            and game_map.terrain[grid_x][grid_y].seen \
            and constants['map_width'] <= mouse_x < constants['display_width'] - 1 \
            and 0 <= mouse_y <= constants['view_height']:
        
        if game_map.terrain[grid_x][grid_y].elevation >= Elevation.DEEPS:
            location_name = "X:{} Y:{}".format(grid_x, grid_y)
            location_text = constants['font'].render(location_name, 1, constants['colors']['text'])
            w, h = constants['font'].size(location_name)
            if width < w:
                width = w
            vertical += h
            location_surf = pygame.Surface((w, h))
            location_surf.blit(location_text, (0, 0))
            
            terrain_name = game_map.terrain[grid_x][grid_y].name
            terrain_text = constants['font'].render(terrain_name, 1, constants['colors']['text'])
            w, h = constants['font'].size(terrain_name)
            if w > width:
                width = w
            vertical += h
            terrain_surf = pygame.Surface((w, h))
            terrain_surf.blit(terrain_text, (0, 0))
            
            if game_map.terrain[grid_x][grid_y].decoration:
                decor_name = game_map.terrain[grid_x][grid_y].decoration.name
                decor_text = constants['font'].render(decor_name, 1, constants['colors']['text'])
                w, h = constants['font'].size(decor_name)
                if w > width:
                    width = w
                vertical += h
                decor_surf = pygame.Surface((w, h))
                decor_surf.blit(decor_text, (0, 0))
        
        entities_under_mouse = []
        for entity in entities:
            if entity.name is not 'player' \
                    and (0 <= entity.x < game_map.width) \
                    and (0 <= entity.y < game_map.height) \
                    and (entity.x, entity.y) in player.view.fov \
                    and (entity.x, entity.y) == (grid_x, grid_y) \
                    and entity.icon:
                entities_under_mouse.append(entity)
        if len(entities_under_mouse) > 0:
            height = 0
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
            vert = constants['margin']
            for entity in entities_under_mouse:
                vert += render_entity_info(entity_surf, entity, constants, vert)
            vertical += entity_surf.get_height()
    
    if location_surf:
        vert = constants['margin']
        info_surf = pygame.Surface((width + 2 * constants['margin'],
                                    vertical + 2 * constants['margin']))
        info_surf.blit(location_surf, (constants['margin'], vert))
        vert += constants['font'].get_height()
        if terrain_surf:
            info_surf.blit(terrain_surf, (constants['margin'], vert))
            vert += constants['font'].get_height()
        if decor_surf:
            info_surf.blit(decor_surf, (constants['margin'], vert))
            vert += constants['font'].get_height()
        if entity_surf:
            info_surf.blit(entity_surf, (constants['margin'], vert))
    
    if info_surf:
        render_border(info_surf, constants['colors']['text'])
    return info_surf


def create_ship_icon(entity, constants):
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
