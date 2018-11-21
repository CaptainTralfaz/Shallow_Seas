import math
from enum import Enum

import pygame

from src.map_objects.map_utils import direction_angle, get_grid_from_coords, hex_to_cube, Hex, get_target_hexes

class RenderOrder(Enum):
    TERRAIN = 1
    DECORATION = 2
    SUNK = 3
    TOWN = 4
    BOAT = 5
    FLYING = 6
    FOG = 7


def render_display(display, game_map, player, entities, constants, mouse_x, mouse_y, message_log, targeting=False):
    display.fill(constants['colors']['black'])
    
    board_surf = render_board(game_map, player, entities, constants, targeting)
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

    y = message_surf.get_height() - constants['font'].get_linesize() * (len(message_log.messages) + 1)
    for message in message_log.messages:
        y += constants['font'].get_linesize()
        message_text = constants['font'].render(str(message.text), 1, message.color)
        message_surf.blit(message_text, (0, y))
        message_rect = message_text.get_rect()
        message_rect.centerx = message_surf.get_width() // 2

    border_panel = pygame.Surface((constants['message_width'], constants['message_height']))
    
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(message_surf, (constants['margin'], constants['margin']))
    return border_panel


def render_board(game_map, player, entities, constants, targeting):
    game_map_surf = pygame.Surface((constants['board_width'] * constants['tile_size'] - 2 * constants['margin'],
                                    constants['board_height'] * constants['tile_size'] - constants['half_tile']))
    
    target_hexes = []
    if targeting:
        target_hexes = get_target_hexes(game_map, player, constants['icons'])
        
    for x in range(player.x - 10, player.x + 11):
        for y in range(player.y - 10, player.y + 11):
            if (0 <= x < game_map.width) and (0 <= y < game_map.height) and game_map.seen[x][y]:
                if game_map.terrain[x][y] == 0:
                    icon = constants['icons']['deeps']
                elif game_map.terrain[x][y] == 1:
                    icon = constants['icons']['water']
                elif game_map.terrain[x][y] == 2:
                    icon = constants['icons']['shallows']
                elif game_map.terrain[x][y] == 3:
                    icon = constants['icons']['sand']
                elif game_map.terrain[x][y] == 4:
                    icon = constants['icons']['grass']
                elif game_map.terrain[x][y] == 5:
                    icon = constants['icons']['forest']
                elif game_map.terrain[x][y] == 6:
                    icon = constants['icons']['mountain']
                else:
                    icon = constants['icons']['volcano']
                game_map_surf.blit(icon, (x * constants['tile_size'] - 10,
                                          y * constants['tile_size'] + x % 2 * constants['half_tile']
                                          - constants['half_tile'] - 10))
                if (x, y) in target_hexes:
                    icon = constants['icons']['highlight']
                    game_map_surf.blit(icon, (x * constants['tile_size'] - 10,
                                              y * constants['tile_size'] + x % 2 * constants['half_tile']
                                              - constants['half_tile'] - 10))
                    
    for decoration in game_map.decorations:
        icon = constants['icons']['water']
        (x, y) = decoration['location']
        if (player.x - 9 < x < player.x + 10) and \
                (player.y - 10 < y < player.y + 11) and \
                game_map.seen[x][y]:
            if decoration['name'] == 'rocks':
                icon = constants['icons']['rocks']
            elif decoration['name'] == 'sandbar':
                icon = constants['icons']['sandbar']
            elif decoration['name'] == 'coral':
                icon = constants['icons']['coral']
            elif decoration['name'] == 'seaweed':
                icon = constants['icons']['seaweed']
            elif decoration['name'] == 'town':
                icon = constants['icons']['town']
            elif decoration['name'] == 'salvage':
                icon = constants['icons']['salvage']
            game_map_surf.blit(icon, (x * constants['tile_size'] - 5,
                                      y * constants['tile_size'] + (x % 2) * constants['half_tile']
                                      - constants['half_tile']))
    
    icon = create_ship_icon(player, constants)
    game_map_surf.blit(rot_center(icon, direction_angle[player.mobile.direction]),
                       (player.x * constants['tile_size'] - 5,
                        player.y * constants['tile_size'] + player.x % 2 * constants['half_tile']
                        - constants['half_tile']))
    
    for entity in entities:
        if (0 <= entity.x < game_map.width) \
                and (0 <= entity.y < game_map.height) \
                and (entity.x, entity.y) in player.view.fov:
            if hasattr(entity, 'mast_sail'):
                icon = create_ship_icon(entity, constants)
            else:
                icon = entity.icon
            game_map_surf.blit(rot_center(icon, direction_angle[entity.mobile.direction]),
                               (entity.x * constants['tile_size'] - 5,
                                entity.y * constants['tile_size'] + entity.x % 2 * constants['half_tile']
                                - constants['half_tile']))
    
    for x in range(player.x - 10, player.x + 11):
        for y in range(player.y + 10, player.y - 11, -1):
            if (0 <= x < game_map.width) \
                    and (0 <= y < game_map.height) \
                    and game_map.seen[x][y] \
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
    status_panel.fill(constants['colors']['black'])
    vertical = 0
    font_size = constants['font'].get_height()

    # wind direction
    direction_text = constants['font'].render('Wind Direction:', 1, constants['colors'].get('text'))
    direction_rect = direction_text.get_rect()
    direction_rect.midleft = (constants['margin'], constants['half_tile'])
    status_panel.blit(direction_text, direction_rect)
    status_panel.blit(constants['icons']['compass'],
                      (constants['status_width'] - constants['tile_size'] - 2 * constants['margin'], 0))
    if game_map.wind_direction is not None:
        status_panel.blit(rot_center(constants['icons']['arrow'], direction_angle[game_map.wind_direction]),
                          (constants['status_width'] - constants['tile_size'] - 2 * constants['margin'], 0))
    vertical += font_size * 2
    # vertical += font_size + constants['margin']
    
    vertical += render_ship_info(status_panel, player, constants, vertical)
    
    grid_x, grid_y = get_grid_from_coords((mouse_x, mouse_y), (player.x, player.y), constants)
    
    if (0 <= grid_x < game_map.width) \
            and (0 <= grid_y < game_map.height) \
            and constants['map_width'] <= mouse_x < constants['display_width'] - 1 \
            and 0 <= mouse_y <= constants['view_height']:
        render_mouse_coords(status_panel, constants, grid_x, grid_y)
    
    if (0 <= grid_x < game_map.width) \
            and (0 <= grid_y < game_map.height) \
            and game_map.seen[grid_x][grid_y] \
            and constants['map_width'] <= mouse_x < constants['display_width'] - 1 \
            and 0 <= mouse_y <= constants['view_height']:
        text = None
        if game_map.terrain[grid_x][grid_y] == 0:
            text = "Ocean"
        elif game_map.terrain[grid_x][grid_y] == 1:
            text = "Sea"
        elif game_map.terrain[grid_x][grid_y] == 2:
            text = "Shallows"
        elif game_map.terrain[grid_x][grid_y] == 3:
            text = "Dunes"
        elif game_map.terrain[grid_x][grid_y] == 4:
            text = "Grassland"
        elif game_map.terrain[grid_x][grid_y] == 5:
            text = "Jungle"
        elif game_map.terrain[grid_x][grid_y] == 6:
            text = "Mountain"
        elif game_map.terrain[grid_x][grid_y] > 6:
            text = "Volcano"
        if text:
            text_cube = hex_to_cube(Hex(grid_x, grid_y))
            decor_text = constants['font'].render("{} X:{} Y:{} Z:{}".format(text, text_cube.x,
                                                                             text_cube.y, text_cube.z), 1,
                                                  constants['colors'].get('text'))
            decor_rect = decor_text.get_rect()
            decor_rect.center = (constants['status_width'] // 2,
                                 constants['status_height'] - 2 * constants['font'].get_height())
            status_panel.blit(decor_text, decor_rect)
        
        for entity in entities:
            if (0 <= entity.x < game_map.width) \
                    and (0 <= entity.y < game_map.height) \
                    and (entity.x, entity.y) in player.view.fov \
                    and (entity.x, entity.y) == (grid_x, grid_y):
                vertical = font_size + constants['margin'] + render_ship_info(status_panel, entity, constants, vertical)
        
        for decor in game_map.decorations:
            if decor['location'] == (grid_x, grid_y):
                decor_text = constants['font'].render(decor['name'].capitalize(), 1,
                                                      constants['colors'].get('text'))
                decor_rect = decor_text.get_rect()
                decor_rect.center = (constants['status_width'] // 2,
                                     constants['status_height'] - constants['font'].get_height())
                status_panel.blit(decor_text, decor_rect)
    
    border_panel = pygame.Surface((constants['status_width'],
                                   constants['status_height']))
    render_border(border_panel, constants['colors']['text'])
    
    border_panel.blit(status_panel, (constants['margin'], constants['margin']))
    return border_panel


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
    font_size = constants['font'].get_height()
    # ship status
    
    # ship name
    cube = hex_to_cube(Hex(entity.x, entity.y))
    name_text = constants['font'].render("{} X:{} Y:{} Z:{}".format(entity.name, cube.x, cube.y, cube.z), 1,
                                         constants['colors'].get('text'))
    name_rect = name_text.get_rect()
    name_rect.center = (constants['status_width'] // 2, vertical + constants['half_tile'])
    status_panel.blit(name_text, name_rect)
    vertical += font_size + constants['margin']
    
    # ship sails
    if hasattr(entity, 'mast_sail') and entity.mast_sail.masts > 0:
        sail_text = constants['font'].render(
            'Sails Raised:  {} / {}'.format(entity.mast_sail.current_sails, entity.mast_sail.max_sails), 1,
            constants['colors'].get('text'))
        sail_rect = sail_text.get_rect()
        sail_rect.midleft = (constants['margin'], vertical + constants['half_tile'])
        sail_max_bar = pygame.Surface(
            (status_panel.get_width() - 2 * constants['margin'], constants['font'].get_height()))
        sail_max_bar.fill(constants['colors'].get('dark_blue'))
        bar_length = math.floor(float(entity.mast_sail.current_sails / entity.mast_sail.max_sails *
                                      (status_panel.get_width() - 2 * constants['margin'])))
        if bar_length < 0:
            bar_length = 0
        sail_bar = pygame.Surface((bar_length, constants['font'].get_height()))
        sail_bar.fill(constants['colors'].get('light_blue'))
        sail_max_bar.blit(sail_bar, (0, 0))
        status_panel.blit(sail_max_bar, sail_rect)
        status_panel.blit(sail_text, sail_rect)
        vertical += font_size + constants['margin']
    
    # ship momentum
    momentum_text = constants['font'].render('Momentum:  {} / {}'.format(entity.mobile.current_momentum,
                                                                         entity.mobile.max_momentum),
                                             1, constants['colors'].get('text'))
    momentum_rect = momentum_text.get_rect()
    momentum_rect.midleft = (constants['margin'], vertical + constants['half_tile'])
    momentum_max_bar = pygame.Surface((status_panel.get_width() - 2 * constants['margin'],
                                       constants['font'].get_height()))
    momentum_max_bar.fill(constants['colors'].get('dark_red'))
    bar_length = math.floor(float(entity.mobile.current_momentum / entity.mobile.max_momentum *
                                  (status_panel.get_width() - 2 * constants['margin'])))
    if bar_length < 0:
        bar_length = 0
    momentum_bar = pygame.Surface((bar_length, constants['font'].get_height()))
    momentum_bar.fill(constants['colors'].get('light_red'))
    momentum_max_bar.blit(momentum_bar, (0, 0))
    status_panel.blit(momentum_max_bar, momentum_rect)
    status_panel.blit(momentum_text, momentum_rect)
    vertical += font_size + constants['margin']
    
    # ship speed
    speed_text = constants['font'].render('Speed:  {} / {}'.format(entity.mobile.current_speed,
                                                                   entity.mobile.max_speed), 1,
                                          constants['colors'].get('text'))
    speed_rect = speed_text.get_rect()
    speed_rect.midleft = (constants['margin'], vertical + constants['half_tile'])
    speed_max_bar = pygame.Surface((status_panel.get_width() - 2 * constants['margin'], constants['font'].get_height()))
    speed_max_bar.fill(constants['colors'].get('dark_green'))
    bar_length = math.floor(float(entity.mobile.current_speed / entity.mobile.max_speed *
                                  (status_panel.get_width() - 2 * constants['margin'])))
    if bar_length < 0:
        bar_length = 0
    speed_bar = pygame.Surface((bar_length, constants['font'].get_height()))
    speed_bar.fill(constants['colors'].get('light_green'))
    speed_max_bar.blit(speed_bar, (0, 0))
    status_panel.blit(speed_max_bar, speed_rect)
    status_panel.blit(speed_text, speed_rect)
    vertical += font_size + constants['margin']
    
    return vertical


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
    block = pygame.Surface(constants['map_block'])
    block.fill(constants['colors']['light_blue'])
    for x in range(constants['board_width']):
        for y in range(constants['board_height']):
            if game_map.seen[x][y]:
                if game_map.terrain[x][y] == 0:
                    block.fill(constants['colors']['light_blue'])
                elif game_map.terrain[x][y] == 1:
                    block.fill(constants['colors']['blue'])
                elif game_map.terrain[x][y] == 2:
                    block.fill(constants['colors']['aqua'])
                elif game_map.terrain[x][y] == 3:
                    block.fill(constants['colors']['cantaloupe'])
                elif game_map.terrain[x][y] == 4:
                    block.fill(constants['colors']['light_green'])
                elif game_map.terrain[x][y] == 5:
                    block.fill(constants['colors']['medium_green'])
                elif game_map.terrain[x][y] == 6:
                    block.fill(constants['colors']['text'])
                elif game_map.terrain[x][y] >= 7:
                    block.fill(constants['colors']['red'])
                if (x, y) == game_map.towns:
                    block.fill(constants['colors']['purple'])
                map_surf.blit(block, (x * constants['block_size'],
                                      y * constants['block_size'] + (x % 2) * (constants['block_size'] // 2)
                                      - constants['block_size'] // 2))
    
    small_block = pygame.Surface((constants['block_size'] // 2, constants['block_size'] // 2))
    for decoration in game_map.decorations:
        x, y = decoration['location']
        if game_map.seen[x][y]:
            if decoration['name'] == 'rocks':
                small_block.fill(constants['colors']['text'])
            elif decoration['name'] == 'sandbar':
                small_block.fill(constants['colors']['cantaloupe'])
            elif decoration['name'] == 'coral':
                small_block.fill(constants['colors']['carnation'])
            elif decoration['name'] == 'seaweed':
                small_block.fill(constants['colors']['medium_green'])
            else:
                small_block.fill(constants['colors']['red'])
            map_surf.blit(small_block, (x * constants['block_size'] + 1,
                                        y * constants['block_size'] + (x % 2) * (constants['block_size'] // 2) + 1
                                        - constants['block_size'] // 2))
    
    block.fill(constants['colors']['white'])
    map_surf.blit(block, (player.x * constants['block_size'],
                          player.y * constants['block_size'] + (player.x % 2) * (constants['block_size'] // 2)
                          - constants['block_size'] // 2))
    for entity in entities:
        if (0 <= entity.x < game_map.width) and (0 <= entity.y < game_map.height) \
                and (entity.x, entity.y) in player.view.fov:
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
    name = 'ship_' + str(entity.size.size) + '_mast'
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
