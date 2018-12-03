import math
from enum import Enum

import pygame

from src.game_states import GameStates
from src.map_objects.map_utils import direction_angle, get_grid_from_coords, get_target_hexes
from src.map_objects.tile import Elevation


class RenderOrder(Enum):
    TERRAIN = 1
    DECORATION = 2
    SUNK = 3
    PORT = 4
    BOAT = 5
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
    status_surf = render_status(game_map, player, entities, constants, mouse_x, mouse_y)
    display.blit(status_surf, (0, constants['map_height']))
    
    message_surf = render_messages(message_log, constants)
    display.blit(message_surf, (constants['status_width'], constants['view_height']))
    
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
    
    for entity in entities:
        if (0 <= entity.x < game_map.width) \
                and (0 <= entity.y < game_map.height) \
                and (entity.x, entity.y) in player.view.fov:
            if entity.mast_sail:
                icon = create_ship_icon(entity, constants)
            else:
                icon = entity.icon
            
            game_map_surf.blit(rot_center(icon, direction_angle[entity.mobile.direction]),
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


def render_status(game_map, player, entities, constants, mouse_x, mouse_y):
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
        status_panel.blit(rot_center(constants['icons']['arrow'], direction_angle[game_map.wind_direction]),
                          (constants['status_width'] - 2 * constants['tile_size'] + constants['margin'],
                           2 * constants['margin']))
    vertical = constants['tile_size']
    
    vertical = render_ship_info(status_panel, player, constants, vertical)
    
    grid_x, grid_y = get_grid_from_coords((mouse_x, mouse_y), (player.x, player.y), constants)
    
    if (0 <= grid_x < game_map.width) \
            and (0 <= grid_y < game_map.height) \
            and game_map.terrain[grid_x][grid_y].seen \
            and constants['map_width'] <= mouse_x < constants['display_width'] - 1 \
            and 0 <= mouse_y <= constants['view_height']:
        text = None
        if game_map.terrain[grid_x][grid_y].elevation >= Elevation.DEEPS:
            text = game_map.terrain[grid_x][grid_y].name
        if text:
            decor_text = constants['font'].render("{} X:{} Y:{}".format(text, grid_x, grid_y), 1,
                                                  constants['colors'].get('text'))
            decor_rect = decor_text.get_rect()
            decor_rect.center = (constants['status_width'] // 2,
                                 constants['status_height'] - 2 * constants['font'].get_height())
            status_panel.blit(decor_text, decor_rect)

        for entity in entities:
            if entity.name is not 'player' \
                    and (0 <= entity.x < game_map.width) \
                    and (0 <= entity.y < game_map.height) \
                    and (entity.x, entity.y) in player.view.fov \
                    and (entity.x, entity.y) == (grid_x, grid_y):
                vertical = render_ship_info(status_panel, entity, constants, vertical)
        
        if game_map.terrain[grid_x][grid_y].decoration:
            decor_text = constants['font'].render(game_map.terrain[grid_x][grid_y].decoration.name, 1,
                                                  constants['colors']['text'])
            decor_rect = decor_text.get_rect()
            decor_rect.center = (constants['status_width'] // 2,
                                 constants['status_height'] - constants['font'].get_height())
            status_panel.blit(decor_text, decor_rect)
    
    border_panel = pygame.Surface((constants['status_width'],
                                   constants['status_height']))
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(status_panel, (constants['margin'], constants['margin']))
    return border_panel


def render_weapons(status_panel, entity, constants, vertical):
    for weapon in entity.weapons.weapon_list:
        if weapon.current_cd == 0:
            color = constants['colors']['text']
        else:
            color = constants['colors']['gray']
        weapon_text = constants['font'].render("{} {}  [{}]".format(weapon.location, weapon.name, weapon.current_cd),
                                               1, color)
        status_panel.blit(weapon_text, (constants['margin'], vertical))
        hp_text = constants['font'].render("{}/{}".format(weapon.current_sp, weapon.max_sp),
                                           1, color)
        status_panel.blit(hp_text, (status_panel.get_width() - constants['margin'] - hp_text.get_width(),
                                    vertical))
        vertical += constants['font'].get_height()
    return vertical


def render_mouse_coords(status_panel, constants, grid_x, grid_y):
    xy_text = constants['font'].render('X: {}, Y: {}'.format(grid_x, grid_y), 1, constants['colors'].get('text'))
    xy_rect = xy_text.get_rect()
    xy_rect.center = (status_panel.get_width() // 2, xy_text.get_height() * 2)
    status_panel.blit(xy_text, xy_rect)


def render_border(panel, color):
    pygame.draw.lines(panel, color, True,
                      ((2, 2),
                       (panel.get_width() - 3, 2),
                       (panel.get_width() - 3, panel.get_height() - 3),
                       (2, panel.get_height() - 3)), 1)


def render_ship_info(status_panel, entity, constants, vertical):
    font = constants['font']
    # ship name
    vertical += font.get_height()
    
    name_text = font.render("{} X:{} Y:{}".format(entity.name, entity.x, entity.y), 1, constants['colors']['text'])
    status_panel.blit(name_text, (constants['margin'] + 1, vertical + 1))
    vertical += font.get_height()
    
    if entity.mast_sail and entity.mast_sail.masts > 0:
        status_panel.blit(make_bar('Sails', font, constants['colors']['text'],
                                   entity.mast_sail.current_sails, entity.mast_sail.max_sails,
                                   constants['colors']['light_blue'], constants['colors']['dark_blue'],
                                   status_panel.get_width() - 2 * constants['margin']),
                          (constants['margin'], vertical))
        vertical += font.get_height() + constants['margin'] // 2
    status_panel.blit(make_bar('Momentum', font, constants['colors']['text'],
                               entity.mobile.current_momentum, entity.mobile.max_momentum,
                               constants['colors']['light_red'], constants['colors']['dark_red'],
                               status_panel.get_width() - 2 * constants['margin']),
                      (constants['margin'], vertical))
    vertical += font.get_height() + constants['margin'] // 2
    status_panel.blit(make_bar('Speed', font, constants['colors']['text'],
                               entity.mobile.current_speed, entity.mobile.max_speed,
                               constants['colors']['light_green'], constants['colors']['dark_green'],
                               status_panel.get_width() - 2 * constants['margin']),
                      (constants['margin'], vertical))
    vertical += font.get_height() + constants['margin'] // 2
    if entity.weapons:
        vertical = render_weapons(status_panel, entity, constants, vertical)

    return vertical


def make_bar(text, font, font_color, current, maximum, top_color, bottom_color, bar_width):
    max_bar = pygame.Surface((bar_width, font.get_height()))
    max_bar.fill(bottom_color)
    current_bar_length = math.floor(float(current / maximum * bar_width))
    if current_bar_length < 0:
        current_bar_length = 0
    current_bar = pygame.Surface((current_bar_length, font.get_height()))
    current_bar.fill(top_color)
    bar_text = font.render('{}:  {} / {}'.format(text, current, maximum), 1, font_color)
    max_bar.blit(current_bar, (0, 0))
    max_bar.blit(bar_text, (1, 1))
    
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
                and (entity.x, entity.y) in player.view.fov:
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
