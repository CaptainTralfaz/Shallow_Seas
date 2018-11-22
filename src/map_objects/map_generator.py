from queue import Queue
from random import randint

from src.map_objects.map_utils import hex_directions, get_hex_land_neighbors
from src.map_objects.tile import Terrain, Decoration, Elevation


def generate_terrain(game_map, island_size: int, max_seeds: int):
    """
    Generates the terrain on the map
    :param game_map: GameMap - the current map
    :param island_size: int - maximum steps for walking
    :param max_seeds: maximum number of paths that will be drunk-walked to create island chains
    :return: None
    """
    num_seeds = randint(max_seeds // 2, max_seeds)
    seeds = get_seed_locations(width=game_map.width, height=game_map.height, num=num_seeds)
    height_map = [[0 for y in range(game_map.height)] for x in range(game_map.width)]

    for seed in seeds:
        size = randint(island_size // 2, island_size)
        x, y = seed
        for i in range(size):
            move = randint(0, len(hex_directions))
            if move == len(hex_directions):
                dx = 0
                dy = 0
            else:
                dx, dy = hex_directions[move]
                if dx != 0:
                    dy += x % 2
            # make sure direction is not out of bounds (leaving a 1 tile margin around map)
            if game_map.in_bounds(x + dx, y + dy, margin=1):
                x = x + dx
                y = y + dy
                height_map[x][y] += 1
    
    islands = find_all_islands(height_map, game_map.width, game_map.height)
    largest, largest_islands = get_largest_islands(islands)

    town_x = None
    town_y = None
    for island in islands:
        for tile in island:
            tile_x, tile_y = tile
            for direction in hex_directions:
                dx, dy = direction
                x = dx + tile_x
                if dx == 0:
                    y = dy + tile_y
                else:
                    y = dy + tile_y + tile_x % 2
                if (0 <= x < game_map.width) and (0 <= y < game_map.height) and height_map[x][y] == 0:
                    height_map[x][y] += 1
        
        if len(island) == largest and not (town_x or town_y):
            valid_tiles = remove_bad_tiles(height_map, island)
            print(valid_tiles)
            town_x, town_y = valid_tiles[randint(0, len(valid_tiles) - 1)]
            print(town_x, town_y)
            
    for x in range(game_map.width):
        for y in range(game_map.height):
            if height_map[x][y] > 7:
                height_map[x][y] = 7
            game_map.terrain[x][y] = Terrain(x=x, y=y, elevation=Elevation(height_map[x][y]))
            if x == town_x and y == town_y:
                game_map.terrain[town_x][town_y].decoration = Decoration('Town')


def remove_bad_tiles(height_map, island):
    choices = []
    for (x, y) in island:
        # make sure elevation is sand, grass, or jungle, and make sure there is at least 1 water next to tile
        if (3 <= height_map[x][y] <= 5) and len(get_hex_land_neighbors(height_map, x, y)) < 6:
            choices.append((x, y))
    return choices


def get_seed_locations(width: int, height: int, num: int):
    seeds = []
    for i in range(num):
        x = randint(4, width - 5)
        y = randint(4, height - 5)
        seeds.append((x, y))
    return seeds


def get_largest_islands(islands):
    largest_islands = []
    largest_length = 0
    for island in islands:
        if len(island) > largest_length:
            largest_length = len(island)
    for island in islands:
        if len(island) == largest_length:
            largest_islands.append(island)
    print(largest_islands)
    return largest_length, largest_islands


def find_all_islands(height_map, width, height):
    island_tiles = []  # holds set of all coordinates in island found so far
    explored = []
    island_list = []
    for x in range(1, width - 2):
        for y in range(1, height - 2):
            if (x, y) not in island_tiles and (x, y) not in explored and height_map[x][y] > 2:
                # found a land tile, so...
                #  get all tiles in this island
                new_island_tiles = explore_hex_island_iterative(height_map, x, y)
                explored.extend(new_island_tiles)
                island_list.append(new_island_tiles)
                # print(island_list)
    return island_list


def explore_hex_island_iterative(game_map, x, y):
    frontier = Queue()
    frontier.put((x, y))
    visited = [(x, y)]
    
    while not frontier.empty():
        current = frontier.get()
        x, y = current
        for neighbor in get_hex_land_neighbors(game_map, x, y):
            if neighbor not in visited:
                frontier.put(neighbor)
                visited.append(neighbor)
    return visited
