import pygame


def get_constants():
    frames_per_second = 60  # frames per second, the general speed of the program
    tick = 2  # number of minutes of game time that pass each turn
    
    margin = 5
    tab = 75
    
    display_title = 'Shallow Seas'
    display_width = 800
    display_height = 800
    
    map_width = 202  # includes margins
    map_height = 200  # includes margins
    block_size = 3
    map_block = (block_size, block_size)
    
    view_width = display_width - map_width  # includes margins
    view_height = 618  # includes margins

    control_width = map_width
    control_height = display_height - view_height
    
    status_width = map_width  # includes margins
    status_height = display_height - map_height - control_height # includes margins
    
    message_width = display_width - map_width  # includes margins
    message_height = display_height - view_height  # includes margins
    message_panel_size = 9
    log_size = 50

    board_width = 64
    board_height = board_width
    island_size = board_height // 2
    island_seeds = board_height
    
    font = pygame.font.Font('freesansbold.ttf', 16)
    # font = pygame.font.Font('/Users/brianhaler/PycharmProjects/Shallow_Seas/src/data/fonts/joystix-monospace.ttf', 10)

    max_entities = board_width // 4
    
    tile_size = 32
    half_tile = tile_size // 2
    
    colors = {
        'text': (200, 200, 200),
        'black': (0, 0, 0),
        'dark_gray': (25, 25, 25),
        'gray': (150, 150, 150),
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
        'amber': (200, 150, 40),
    }
    
    icons = {
        # misc game icons 32x32
        'game_icon': pygame.image.load('icons/misc/Compass.png'),
        'shade': pygame.image.load('icons/misc/Shade.png'),
        'highlight': pygame.image.load('icons/misc/Highlight.png'),
        'pointer': pygame.image.load('icons/misc/Pointer.png'),
        'compass': pygame.image.load('icons/misc/Compass.png'),
        'arrow': pygame.image.load('icons/misc/Arrow.png'),
        'fog': pygame.image.load('icons/misc/Fog.png'),
        'calm': pygame.image.load('icons/misc/Sky.png'),
        'hazy': pygame.image.load('icons/misc/Haze.png'),
        'cloudy': pygame.image.load('icons/misc/Cloud.png'),
        'rainy': pygame.image.load('icons/misc/Rain.png'),
        'stormy': pygame.image.load('icons/misc/Storm.png'),
        # misc game icons 16x16
        'sun': pygame.image.load('icons/misc/Sun.png'),
        'moon': pygame.image.load('icons/misc/Moon.png'),
        'moon_shadow': pygame.image.load('icons/misc/MoonShadow.png'),
        # terrain icons 42x42
        'deep_sea': pygame.image.load('icons/terrain/DeepSea.png'),
        'sea': pygame.image.load('icons/terrain/Sea.png'),
        'shallows': pygame.image.load('icons/terrain/Shallows.png'),
        'dunes': pygame.image.load('icons/terrain/Dunes.png'),
        'swamp': pygame.image.load('icons/terrain/Swamp.png'),
        'grassland': pygame.image.load('icons/terrain/Grassland.png'),
        'jungle': pygame.image.load('icons/terrain/Jungle.png'),
        'mountain': pygame.image.load('icons/terrain/Mountain.png'),
        'volcano': pygame.image.load('icons/terrain/Volcano.png'),
        # entity icons 32x32
        'ship_0_mast': pygame.image.load('icons/entities/Ship_0_mast.png'),
        'ship_1_mast': pygame.image.load('icons/entities/Ship_1_mast.png'),
        'ship_2_mast': pygame.image.load('icons/entities/Ship_2_mast.png'),
        'ship_3_mast': pygame.image.load('icons/entities/Ship_3_mast.png'),
        'ship_4_mast': pygame.image.load('icons/entities/Ship_4_mast.png'),
        'port': pygame.image.load('icons/entities/Port.png'),
        'seaweed': pygame.image.load('icons/entities/Seaweed.png'),
        'sandbar': pygame.image.load('icons/entities/Sandbar.png'),
        'rocks': pygame.image.load('icons/entities/Rocks.png'),
        'coral': pygame.image.load('icons/entities/Coral.png'),
        'salvage': pygame.image.load('icons/entities/Salvage.png'),
        'sea_serpent': pygame.image.load('icons/entities/SeaSerpent.png'),
        'sea_turtle': pygame.image.load('icons/entities/SeaTurtle.png'),
        'red_dragon': pygame.image.load('icons/entities/RedDragon.png'),
        'wyvern': pygame.image.load('icons/entities/Wyvern.png'),
        'giant_bat': pygame.image.load('icons/entities/GiantBat.png'),
        'carcass': pygame.image.load('icons/entities/Carcass.png'),
        'sunken_ship': pygame.image.load('icons/entities/SunkenShip.png'),
        # inventory icons 16x16
        'bat_wing': pygame.image.load('icons/inventory/BatWing.png'),
        'brick': pygame.image.load('icons/inventory/Brick.png'),
        'canvas': pygame.image.load('icons/inventory/Canvas.png'),
        'fish': pygame.image.load('icons/inventory/Fish.png'),
        'fruit': pygame.image.load('icons/inventory/Fruit.png'),
        'leather': pygame.image.load('icons/inventory/Leather.png'),
        'meat': pygame.image.load('icons/inventory/Meat.png'),
        'obsidian': pygame.image.load('icons/inventory/Obsidian.png'),
        'pearl': pygame.image.load('icons/inventory/Pearl.png'),
        'rope': pygame.image.load('icons/inventory/Rope.png'),
        'rum': pygame.image.load('icons/inventory/Rum.png'),
        'salt': pygame.image.load('icons/inventory/Salt.png'),
        'serpent_scale': pygame.image.load('icons/inventory/SerpentScale.png'),
        'skins': pygame.image.load('icons/inventory/Skins.png'),
        'stone': pygame.image.load('icons/inventory/Stone.png'),
        'turtle_shell': pygame.image.load('icons/inventory/TurtleShell.png'),
        'water': pygame.image.load('icons/inventory/Water.png'),
        'wood': pygame.image.load('icons/inventory/wood.png'),
    }
    
    constants = {
        'FPS': frames_per_second,
        'tick': tick,
        'display_title': display_title,
        'display_width': display_width,
        'display_height': display_height,
        'status_width': status_width,
        'status_height': status_height,
        'control_width': control_width,
        'control_height': control_height,
        'message_width': message_width,
        'message_height': message_height,
        'message_panel_size': message_panel_size,
        'log_size': log_size,
        'margin': margin,
        'tab': tab,
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
