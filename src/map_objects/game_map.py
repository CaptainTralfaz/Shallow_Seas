from random import randint

from src.components.ai import PeacefulMonster, MeleeMonster
from src.components.cargo import Cargo, ItemCategory, Item
from src.components.fighter import Fighter
from src.components.mobile import Mobile
from src.components.size import Size
from src.components.view import View
from src.components.wings import Wings
from src.entity import Entity
from src.map_objects.map_generator import generate_terrain
from src.map_objects.map_utils import hex_directions
from src.map_objects.tile import Decoration, Elevation
from src.render_functions import RenderOrder
from src.weather import weather_effects


class GameMap:
    def __init__(self, width: int, height: int):
        """
        The GameMap object, which holds the game map, map width, map height, wind information, fog map, elevation map
        :param width: width of the game map
        :param height: height of the game map
        """
        self.width = width
        self.height = height
        self.wind_direction = self.starting_wind
        self.wind_turn_count = 0
        self.max_wind_count = 50
        self.terrain = [[None for y in range(height)] for x in range(width)]
        self.fog = self.starting_fog  # Two fogs obscure line of sight
    
    @property
    def starting_wind(self):
        """
        Determines the starting wind:
            None
            or
            0: North,
            1: Northwest,
            2: Southwest,
            3: South,
            4: Southeast,
            5: Northeast
        :return: int wind direction
        """
        wind = randint(0, len(hex_directions))
        if wind == len(hex_directions):
            return None
        else:
            return wind
    
    @property
    def starting_fog(self):
        """
        Determine starting fog map, with a 5% chance for each tile to contain fog
        :return: fog grid of booleans - True where fog is placed
        """
        grid = [[False for y in range(self.height)] for x in range(self.width)]
        base_fog = 5
        for xx in range(self.width):
            for yy in range(self.height):
                fog_chance = randint(0, 99)
                if fog_chance < base_fog:
                    grid[xx][yy] = True
        return grid
    
    def roll_fog(self, game_time, game_weather):
        """
        Moves the fog in the direction of the wind TODO change to cubic coordinates
        :param game_time: current time of day (effects amount of fog)
        :param game_weather: current weather (effects amount of fog)
        :return: None - modifies list of lists object directly
        """
        # move fog with wind direction:
        grid = [[False for y in range(self.height)] for x in range(self.width)]
        if self.wind_direction is not None:
            for x in range(self.width):
                for y in range(self.height):
                    if self.fog[x][y]:
                        dx, dy = hex_directions[self.wind_direction]
                        if self.in_bounds(dx + x, dy + y + (x % 2) * (dx % 2), margin=-1):
                            grid[dx + x][dy + y + (x % 2) * (dx % 2)] = True
            self.fog = grid
            self.add_fog_at_border(game_time, game_weather)
    
    def add_fog_at_border(self, game_time, game_weather):
        """
        Adds fog at each border, percentage chance dependent on weather and time of day
        :param game_time: current Time of day
        :param game_weather: current Weather conditions
        :return: None - modifies list of lists object directly
        """
        north = False
        south = False
        west = False
        east = False
        base_fog = get_base_fog(game_time, game_weather)
        
        if self.wind_direction in [0, 1, 5]:  # wind blowing north, add fog to bottom border
            north = True
        if self.wind_direction in [2, 3, 4]:  # wind blowing south, add fog to top border
            south = True
        if self.wind_direction in [1, 2]:
            west = True
        if self.wind_direction in [4, 5]:
            east = True
        if north:
            for x in range(self.width):
                fog_chance = randint(0, 99)
                if fog_chance < base_fog:
                    self.fog[x][self.height - 1] = True
        if south:
            for x in range(self.width):
                fog_chance = randint(0, 99)
                if fog_chance < base_fog:
                    self.fog[x][0] = True
        if west:
            for y in range(self.height):
                fog_chance = randint(0, 99)
                if fog_chance < base_fog:
                    self.fog[self.width - 1][y] = True
        if east:
            for y in range(self.height):
                fog_chance = randint(0, 99)
                if fog_chance < base_fog:
                    self.fog[0][y] = True
    
    def in_bounds(self, x: int, y: int, margin=0):
        """
        Makes sure a tile (x, y) coordinate is not outside of the map width and height
        TODO: stupid bug here, often have to send "-1" for the margin for this to work correctly
        :param x: int x coordinate of tile
        :param y: int y coordinate of tile
        :param margin: int amount of border around edge of map
        :return: boolean True if coords within map, else False
        """
        if (0 + margin <= x < self.width - 1 - margin) and (0 + margin <= y < self.height - 1 - margin):
            return True
        return False


def make_map(width: int, height: int, entities: list, max_entities: int, icons: dict, islands: int, seeds: int,
             constants: dict, game_time, game_weather):
    """
    Generate map with islands and port
    :param width: int with of game map
    :param height: int height of game map
    :param entities: list of entities
    :param max_entities: Maximum number of entities placed by default
    :param icons: dict of icons
    :param islands: maximum number of islands to create
    :param seeds: list of seeds for the islands
    :param constants: icons, colors, etc.
    :param game_time: current game Time
    :param game_weather: current map weather
    :return: the generated GameMap object
    """
    game_map = GameMap(width=width, height=height)
    generate_terrain(game_map=game_map, island_size=islands, max_seeds=seeds)
    decorate(game_map=game_map)
    place_entities(game_map=game_map, entities=entities, max_entities=max_entities, icons=icons, constants=constants,
                   game_time=game_time, game_weather=game_weather)
    return game_map


def remove_fog(fog, fog_list, width, height):
    """
    randomly removes ~0.5% of fog from the fog map
    :param fog: the fog map coordinate grid
    :param fog_list: list of tiles containing fog
    :param width: width of the fog map
    :param height: height of the fog map
    :return: None - modifies fog map directly
    """
    removal_list = []
    removal_count = (width * height) // 200
    for count in range(removal_count):
        target = randint(0, len(fog_list) - 1)
        removal_list.append(fog_list[target])
    for (x, y) in removal_list:
        fog[x][y] = False


def add_fog(fog, width, height):
    """
    randomly add ~ .5 % of fog to the fog map
    :param fog: the fog map coordinate grid
    :param width: width of the fog map
    :param height: height of the fog map
    :return: None - modifies fog map directly
    """
    fog_add_list = []
    fog_add_count = (width * height) // 200
    for count in range(fog_add_count):
        fog_add_list.append((randint(0, width - 1), randint(0, height - 1)))
    for (x, y) in fog_add_list:
        fog[x][y] = True


def adjust_fog(fog, width, height, game_time, weather):
    """
    Determines if fog should be added or removed from the map depending on Time of day and current Weather conditions
    :param fog: boolean fog map
    :param width: width of fog map
    :param height: height of fog map
    :param game_time: current Time of day
    :param weather: current map Weather
    :return: None - simply directs fog map to correct add/remove method
    """
    target_fog_pct = get_base_fog(game_time=game_time, weather=weather)
    fog_list = [(x, y) for x in range(width) for y in range(height) if fog[x][y]]
    fog_pct = 100 * len(fog_list) // (width * height)
    if target_fog_pct < fog_pct:
        remove_fog(fog=fog, fog_list=fog_list, width=width, height=height)
    elif target_fog_pct > fog_pct:
        add_fog(fog=fog, width=width, height=height)


def get_base_fog(game_time, weather):
    """
    Determine the base % of fog the map should have depending on Time of day and current Weather conditions
    :param game_time: current Time of day
    :param weather: current map Weather
    :return: base % of fog
    """
    base_fog = 0
    base_fog += weather_effects[weather.conditions]['fog']
    base_fog += game_time.get_time_of_day_info['fog']
    return base_fog


def change_wind(game_map: GameMap, message_log, color):
    """
    wind bucket fills up, one per turn.
    chance to change = wind_turn_count/game_map.max_wind_count
    on change:
        if wind not blowing, starts in random direction
        if blowing, can stop, rotate right, or rotate left
    :param game_map: the current map being played on
    :param message_log: list of game messages
    :param color: color of the message
    :return: None
    """
    delay = 10  # leave wind for at least this many turns
    change_chance = randint(0, game_map.max_wind_count)
    if change_chance + delay < game_map.wind_turn_count:
        # change wind 0: dies down / picks up
        #             1: rotate left
        #             2: rotate right
        game_map.wind_turn_count = 0
        if game_map.wind_direction is None:
            # if no wind, wind starts in random direction
            game_map.wind_direction = randint(0, len(hex_directions) - 1)
            game_map.wind_turn_count = 0
            message_log.add_message('Wind picks up.', color)
        else:
            # if wind, 0=die down, 1 = rotate left, 2 = rotate right
            change = randint(0, 4)
            if change == 0:
                # wind dies down
                message_log.add_message('Wind dies down.', color)
                game_map.wind_direction = None
            elif change in [1, 2]:
                # wind rotates right
                message_log.add_message('Wind rotates starboard.', color)
                game_map.wind_direction -= 1
                if game_map.wind_direction < 0:
                    game_map.wind_direction += len(hex_directions)
            elif change in [3, 4]:
                # wind rotates left
                message_log.add_message('Wind rotates port.', color)
                game_map.wind_direction += 1
                if game_map.wind_direction >= len(hex_directions):
                    game_map.wind_direction -= len(hex_directions)
    else:
        game_map.wind_turn_count += 1


def decorate(game_map: GameMap):
    """
    Add decorations to the water tiles of the game map
    TODO: make these do something (turtles swim toward seaweed, rocks damage ships in darkness/storm, etc.)
    :param game_map: the game map
    :return: None - modifies game map terrain decoration field directly
    """
    for x in range(2, game_map.width - 3):
        for y in range(2, game_map.height - 3):
            decor = randint(0, 500)
            if game_map.terrain[x][y].elevation < Elevation.DUNES:
                if 0 <= decor <= 1:
                    game_map.terrain[x][y].decoration = Decoration('Rocks')
                elif 2 <= decor <= 3:
                    game_map.terrain[x][y].decoration = Decoration('Coral')
                elif 4 <= decor <= 6:
                    game_map.terrain[x][y].decoration = Decoration('Sandbar')
                elif 7 <= decor <= 10:
                    game_map.terrain[x][y].decoration = Decoration('Seaweed')
                # elif decor == 500 and randint(0, 9) in [0, 1]:
                #     game_map.terrain[x][y].decoration = Decoration('salvage')


def place_entities(game_map: GameMap, entities: list, max_entities: int, icons: dict, constants: dict,
                   game_time, game_weather):
    """
    Adds entities to the game map
    TODO: add sunken ships, floating chests, new creatures, etc.
    TODO: move entity creation to appropriate factory
    :param game_map: the current game map
    :param entities: current list of entities
    :param max_entities: maximum number of entities to add
    :param icons: icons for the generated entities (will be moved to factory)
    :param constants: dict of constants
    :param game_time: current game Time
    :param game_weather: current map Weather
    :return: None - modify entity list directly
    """
    # Get a random number of entities
    number_of_monsters = randint(2 * max_entities // 3, max_entities + 1)
    
    # This should be
    # 1 choose monster
    # 2 then place - if flying, no location checks, if swimming, try to place until not on land
    
    for i in range(number_of_monsters):
        placed = False
        # Choose a random location
        while not placed:
            x = randint(1, game_map.width - 2)
            y = randint(1, game_map.height - 2)
            if game_map.terrain[x][y].elevation < Elevation.DUNES:
                placed = True
                random_val = randint(0, 100)
                if random_val < 40:
                    size_component = Size.MEDIUM
                    manifest = []
                    manifest.append(Item(name='Turtle Meat', icon=constants['icons']['meat'],
                                         category=ItemCategory.SUPPLIES, weight=.5, volume=.5,
                                         quantity=size_component.value + 1))
                    manifest.append(Item(name='Turtle Shell', icon=constants['icons']['turtle_shell'],
                                         category=ItemCategory.SUPPLIES, weight=2 * size_component.value,
                                         volume=size_component.value, quantity=1))
                    cargo_component = Cargo(max_volume=size_component.value * 10 + 5,
                                            max_weight=size_component.value * 10 + 5, manifest=manifest)
                    view_component = View(size_component.value + 3)
                    mobile_component = Mobile(direction=randint(0, 5), max_momentum=size_component.value * 2 + 2)
                    fighter_component = Fighter("body", size_component.value * 10 + 5)
                    ai_component = PeacefulMonster()
                    npc_icon = icons['sea_turtle']
                    npc = Entity(name='Sea Turtle', x=x, y=y,
                                 size=size_component,
                                 icon=npc_icon,
                                 render_order=RenderOrder.FLOATING,
                                 view=view_component,
                                 mobile=mobile_component,
                                 ai=ai_component,
                                 fighter=fighter_component,
                                 cargo=cargo_component)
                    npc.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
                elif random_val < 70:
                    size_component = Size.TINY
                    manifest = []
                    manifest.append(Item(name='Bat Meat', icon=constants['icons']['meat'],
                                         category=ItemCategory.SUPPLIES, weight=.5, volume=.5,
                                         quantity=size_component.value + 1))
                    manifest.append(Item(name='Bat Wing', icon=constants['icons']['bat_wing'],
                                         category=ItemCategory.EXOTICS, weight=.5, volume=.5,
                                         quantity=(size_component.value + 1) * 2))
                    cargo_component = Cargo(max_volume=size_component.value * 10 + 5,
                                            max_weight=size_component.value * 10 + 5, manifest=manifest)
                    view_component = View(size_component.value + 3)
                    mobile_component = Mobile(direction=randint(0, 5), max_momentum=size_component.value * 2 + 2)
                    fighter_component = Fighter("body", size_component.value * 10 + 5)
                    wing_component = Wings("wings", 2, size_component.value)
                    ai_component = MeleeMonster()
                    npc_icon = icons['giant_bat']
                    npc = Entity(name='Giant Bat', x=x, y=y,
                                 size=size_component,
                                 icon=npc_icon,
                                 render_order=RenderOrder.FLYING,
                                 view=view_component,
                                 mobile=mobile_component,
                                 ai=ai_component,
                                 wings=wing_component,
                                 fighter=fighter_component,
                                 cargo=cargo_component)
                    npc.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
                else:
                    size_component = Size.SMALL
                    manifest = []
                    manifest.append(Item(name='Serpent Meat', icon=constants['icons']['meat'],
                                         category=ItemCategory.SUPPLIES, weight=.5, volume=.5,
                                         quantity=size_component.value + 1))
                    manifest.append(Item(name='Serpent Scale', icon=constants['icons']['serpent_scale'],
                                         category=ItemCategory.EXOTICS, weight=.5, volume=.5,
                                         quantity=size_component.value + 1))
                    cargo_component = Cargo(max_volume=size_component.value * 10 + 5,
                                            max_weight=size_component.value * 10 + 5, manifest=manifest)
                    view_component = View(size_component.value + 3)
                    mobile_component = Mobile(direction=randint(0, 5), max_momentum=size_component.value * 2 + 2)
                    fighter_component = Fighter("body", size_component.value * 10 + 5)
                    ai_component = MeleeMonster()
                    npc_icon = icons['sea_serpent']
                    npc = Entity(name='Sea Serpent', x=x, y=y,
                                 size=size_component,
                                 icon=npc_icon,
                                 render_order=RenderOrder.FLOATING,
                                 view=view_component,
                                 mobile=mobile_component,
                                 ai=ai_component,
                                 fighter=fighter_component,
                                 cargo=cargo_component)
                    npc.view.set_fov(game_map=game_map, game_time=game_time, game_weather=game_weather)
                print('{} placed at {}:{}'.format(npc.name, x, y))
                entities.append(npc)
