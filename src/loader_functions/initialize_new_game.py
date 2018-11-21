import pygame


def get_constants():
    frames_per_second = 30  # frames per second, the general speed of the program
    
    margin = 5
    
    display_title = 'Shallow Seas'
    display_width = 800
    display_height = 800
    
    map_width = 202  # includes margins
    map_height = 200  # includes margins
    block_size = 4
    map_block = (block_size, block_size)
    
    view_width = display_width - map_width  # includes margins
    view_height = 618  # includes margins
    
    status_width = map_width  # includes margins
    status_height = display_height - map_height  # includes margins
    
    message_width = display_width - map_width  # includes margins
    message_height = display_height - view_height  # includes margins
    
    board_width = 48
    board_height = 48
    island_size = board_height // 2
    island_seeds = board_height
    
    font = pygame.font.Font('freesansbold.ttf', 15)
    
    max_entities = 10
    log_size = 10
    
    tile_size = 32
    half_tile = tile_size // 2
    
    colors = {
        'text': (200, 200, 200),
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'light_red': (200, 0, 0),
        'dark_red': (150, 0, 0),
        'orange': (255, 127, 0),
        'bright_yellow': (255, 255, 0),
        'yellow':  (200, 200, 0),
        'green': (0, 255, 0),
        'medium_green': (0, 175, 0),
        'light_green': (0, 125, 0),
        'dark_green': (0, 75, 0),
        'brown': (127, 64, 0),
        'blue': (0, 0, 255),
        'light_blue': (0, 0, 200),
        'dark_blue': (0, 0, 125),
        'aqua': (0, 127, 255),
        'cyan': (0, 255, 255),
        'purple': (255, 0, 255),
        'violet': (127, 0, 255),
        'cantaloupe': (255, 204, 102),
        'carnation': (255, 111, 207),
    }
    
    icons = {
        'game_icon': pygame.image.load('icons/Compass.png'),
        'ship_0_mast': pygame.image.load('icons/Ship_0_mast.png'),
        'ship_1_mast': pygame.image.load('icons/Ship_1_mast.png'),
        'ship_2_mast': pygame.image.load('icons/Ship_2_mast.png'),
        'ship_3_mast': pygame.image.load('icons/Ship_3_mast.png'),
        'ship_4_mast': pygame.image.load('icons/Ship_4_mast.png'),
        'shade': pygame.image.load('icons/Shade.png'),
        'highlight': pygame.image.load('icons/Highlight.png'),
        'deeps': pygame.image.load('icons/Deeps3d.png'),
        'water': pygame.image.load('icons/Water3d.png'),
        'shallows': pygame.image.load('icons/Shallows3d.png'),
        'sand': pygame.image.load('icons/Sand3d.png'),
        'swamp': pygame.image.load('icons/Swamp3d.png'),
        'grass': pygame.image.load('icons/Grass3d.png'),
        'forest': pygame.image.load('icons/Forest3d.png'),
        'mountain': pygame.image.load('icons/Mountain3d.png'),
        'volcano': pygame.image.load('icons/Volcano3d.png'),
        'town': pygame.image.load('icons/Town3d.png'),
        'seaweed': pygame.image.load('icons/Seaweed.png'),
        'sandbar': pygame.image.load('icons/Sandbar.png'),
        'rocks': pygame.image.load('icons/Rocks.png'),
        'coral': pygame.image.load('icons/Coral.png'),
        'fog': pygame.image.load('icons/Fog2.png'),
        'salvage': pygame.image.load('icons/Salvage.png'),
        'arrow': pygame.image.load('icons/Arrow.png'),
        'compass': pygame.image.load('icons/Compass.png'),
        'sea_serpent': pygame.image.load('icons/SeaSerpent.png'),
        'sea_turtle': pygame.image.load('icons/SeaTurtle.png'),
        'red_dragon': pygame.image.load('icons/RedDragon.png'),
    }
    
    constants = {
        'FPS': frames_per_second,
        'display_title': display_title,
        'display_width': display_width,
        'display_height': display_height,
        'status_width': status_width,
        'status_height': status_height,
        'message_width': message_width,
        'message_height': message_height,
        'margin': margin,
        'log_size': log_size,
        'font': font,
        'board_width': board_width,
        'board_height': board_height,
        'island_size': island_size,
        'island_seeds': island_seeds,
        'view_width': view_width,
        'view_height': view_height,
        'map_width': map_width,
        'map_height': map_height,
        'map_block': map_block,
        'block_size': block_size,
        'tile_size': tile_size,
        'half_tile': half_tile,
        'max_entities': max_entities,
        'colors': colors,
        'icons': icons,
    }
    
    return constants

# def get_game_variables(constants):
#     fighter_component = Fighter(hp=100, defense=1, power=2)
#     inventory_component = Inventory(26)
#     equipment_component = Equipment()
#     level_component = Level()
#     player = Entity(15, 5, 5, 'player_sprite', 'Player',
#                     blocks=True,
#                     render_order=RenderOrder.ACTOR,
#                     fighter=fighter_component,
#                     inventory=inventory_component,
#                     level=level_component,
#                     equipment=equipment_component)
#     entities = [player]
#
#     equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
#     dagger = Entity(0, 0, 0, 'dagger_sprite', 'Dagger', equippable=equippable_component)
#     player.inventory.add_item(dagger, constants['colors'])
#     player.equipment.toggle_equip(dagger)
#
#     game_map = Map(constants['map_width'], constants['map_height'])
#     make_map(game_map, constants['room_max_radius'], constants['max_rooms'], player, entities, constants['colors'])
#
#     message_log = MessageLog(constants['log_size'])
#
#     game_state = GameStates.PLAYER_TURN
#
#     return player, entities, game_map, message_log, game_state
