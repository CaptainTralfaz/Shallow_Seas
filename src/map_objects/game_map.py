from random import randint

from src.components.ai import PeacefulMonster, MeleeMonster
from src.components.mobile import Mobile
from src.components.size import Size
from src.components.view import View
from src.entity import Entity
from src.map_objects.map_generator import generate_terrain
from src.map_objects.map_utils import hex_directions
from src.map_objects.tile import Decoration, Elevation


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.wind_direction = self.starting_wind
        self.wind_turn_count = 0
        self.max_wind_count = 50
        self.terrain = [[None for y in range(height)] for x in range(width)]
        
        # TODO: add fog as another cellular automata layer that changes (grows or shrinks) every turn
    
    @property
    def starting_wind(self):
        wind = randint(0, len(hex_directions))
        if wind == len(hex_directions):
            return None
        else:
            return wind
    
    def in_bounds(self, x: int, y: int, margin=0):
        if (0 + margin <= x < self.width - 1 - margin) and (0 + margin <= y < self.height - 1 - margin):
            return True
        return False


def make_map(width: int, height: int, entities: list, max_entities: int, icons: list, islands: int, seeds: int):
    game_map = GameMap(width=width, height=height)
    generate_terrain(game_map, island_size=islands, max_seeds=seeds)
    decorate(game_map)
    place_entities(game_map, entities=entities, max_entities=max_entities, icons=icons)
    return game_map


def change_wind(game_map: GameMap, message_log, color):
    """
    wind bucket fills up, one per turn.
    chance to change = wind_turn_count/game_map.max_wind_count
    on change:
        if wind not blowing, starts in random direction
        if blowing, can stop, rotate right, or rotate left
    :param game_map: the current map being played on
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
    for x in range(2, game_map.width - 3):
        for y in range(2, game_map.height - 3):
            decor = randint(0, 500)
            if game_map.terrain[x][y].elevation.value < Elevation.DUNES.value:
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


def place_entities(game_map: GameMap, entities: list, max_entities: int, icons: dict):
    # Get a random number of entities
    number_of_monsters = randint(max_entities // 2, max_entities + 1)
    
    # This should be
    # 1 choose monster
    # 2 then place - if flying, no location checks, if swimming, try to place until not on land
    
    for i in range(number_of_monsters):
        placed = False
        # Choose a random location
        while not placed:
            x = randint(1, game_map.width - 2)
            y = randint(1, game_map.height - 2)
            if game_map.terrain[x][y].elevation.value < Elevation.DUNES.value:
                placed = True
                # TODO: get these from factory
                if randint(0, 100) < 50:
                    size_component = Size(2)
                    view_component = View(size_component.size + 3)
                    mobile_component = Mobile(direction=randint(0, 5), max_momentum=size_component.size * 2 + 2)
                    ai_component = PeacefulMonster()
                    npc_icon = icons['sea_turtle']
                    npc = Entity(name='Sea Turtle', x=x, y=y,
                                 size=size_component,
                                 icon=npc_icon,
                                 view=view_component,
                                 mobile=mobile_component,
                                 ai=ai_component)
                    npc.view.set_fov(game_map)
                    print('{} placed at {}:{}'.format(npc.name, x, y))
                else:
                    size_component = Size(1)
                    view_component = View(size_component.size + 3)
                    mobile_component = Mobile(direction=randint(0, 5), max_momentum=size_component.size * 2 + 2)
                    ai_component = MeleeMonster()
                    npc_icon = icons['sea_serpent']
                    npc = Entity(name='Sea Serpent', x=x, y=y,
                                 size=size_component,
                                 icon=npc_icon,
                                 view=view_component,
                                 mobile=mobile_component,
                                 ai=ai_component)
                    npc.view.set_fov(game_map)
                    print('{} placed at {}:{}'.format(npc.name, x, y))
                entities.append(npc)
