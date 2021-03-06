import pygame
from random import randint

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
from weather import Weather
from game_time import Time
from render_functions import RenderOrder
from game_states import GameStates
from map_objects.game_map import make_map


def get_constants():
    """
    Holds all the default values for the game
    :return: dict constants
    """
    frames_per_second = 60  # frames per second, the general speed of the program
    tick = 5  # number of minutes of game time that pass each turn
    
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
    status_height = display_height - map_height - control_height  # includes margins
    
    message_width = display_width - map_width  # includes margins
    message_height = display_height - view_height  # includes margins
    message_panel_size = 9
    log_size = 100
    
    board_width = 64
    board_height = board_width
    island_size = board_height // 8 * 5
    island_seeds = board_height
    
    font = pygame.font.Font('freesansbold.ttf', 16)
    
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
        'yellow': (200, 200, 0),
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
        'bread': pygame.image.load('icons/inventory/Breads.png'),
        'brick': pygame.image.load('icons/inventory/Brick.png'),
        'canvas': pygame.image.load('icons/inventory/Canvas.png'),
        'fish': pygame.image.load('icons/inventory/Fish.png'),
        'fruit': pygame.image.load('icons/inventory/Fruit.png'),
        'grain': pygame.image.load('icons/inventory/Grains.png'),
        'leather': pygame.image.load('icons/inventory/Leather.png'),
        'meat': pygame.image.load('icons/inventory/Meat.png'),
        'tar': pygame.image.load('icons/inventory/Tar.png'),
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


def get_game_variables(constants):

    game_time = Time(constants['tick'])
    game_weather = Weather()

    message_log = MessageLog(height=constants['log_size'], panel_size=constants['message_panel_size'], view_pointer=0)

    player_icon = 'ship_1_mast'
    size_component = Size.SMALL
    manifest = []
    manifest.append(Item(name='Canvas', icon='canvas', category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Meat', icon='meat', category=ItemCategory.SUPPLIES,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Pearls', icon='pearl', category=ItemCategory.EXOTICS,
                         weight=0, volume=0, quantity=30))
    manifest.append(Item(name='Rope', icon='rope', category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Tar', icon='tar', category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=5))
    manifest.append(Item(name='Rum', icon='rum', category=ItemCategory.EXOTICS,
                         weight=0.1, volume=2, quantity=2))
    manifest.append(Item(name='Fish', icon='fish', category=ItemCategory.SUPPLIES,
                         weight=0.1, volume=2, quantity=2))
    manifest.append(Item(name='Fruit', icon='fruit', category=ItemCategory.SUPPLIES,
                         weight=0.1, volume=2, quantity=2))
    manifest.append(Item(name='Water', icon='water', category=ItemCategory.SUPPLIES,
                         weight=2, volume=2, quantity=2))
    manifest.append(Item(name='Wood', icon='wood', category=ItemCategory.GOODS,
                         weight=2, volume=2, quantity=5))
    cargo_component = Cargo(max_volume=size_component.value * 10 + 5,
                            max_weight=size_component.value * 10 + 5,
                            manifest=manifest)
    view_component = View(view=size_component.value + 3)
    fighter_component = Fighter(name="hull", max_hps=size_component.value * 10 + 10, repair_with=["Wood", "Tar"])
    weapons_component = WeaponList()
    weapons_component.add_all(size=str(size_component))  # Hacky for now
    mast_component = Masts(name="Mast", masts=size_component.value, size=size_component.value,
                           sail_repair_with=["Canvas", "Rope"], mast_repair_with=["Wood", "Rope"])
    mobile_component = Mobile(direction=0, max_momentum=int(size_component.value) * 2 + 2)
    crew_component = Crew(max_crew=size_component.value * 10 + 5, crew_count=50)
    player = Entity(name='player', x=randint(constants['board_width'] // 4, constants['board_width'] * 3 // 4),
                    y=constants['board_height'] - 1, icon=player_icon, render_order=RenderOrder.PLAYER,
                    view=view_component, size=size_component, mast_sail=mast_component, mobile=mobile_component,
                    weapons=weapons_component, fighter=fighter_component, crew=crew_component, cargo=cargo_component)

    entities = [player]

    game_map = make_map(width=constants['board_width'],
                        height=constants['board_height'],
                        entities=entities,
                        max_entities=constants['max_entities'],
                        islands=constants['island_size'],
                        seeds=constants['island_seeds'],
                        constants=constants,
                        game_time=game_time,
                        game_weather=game_weather)

    player.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
    game_state = GameStates.CURRENT_TURN

    return player, entities, game_map, message_log, game_state, game_weather, game_time
