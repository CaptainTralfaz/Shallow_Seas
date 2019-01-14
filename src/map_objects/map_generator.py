from queue import Queue
from random import randint

from map_objects.map_utils import hex_directions, get_hex_land_neighbors, cube_directions, hex_to_cube, cube_to_hex, \
    cube_add, Hex
from map_objects.tile import Terrain, Decoration, Elevation


def generate_terrain(game_map, island_size: int, max_seeds: int):
    """
    Generates the terrain on the map, and add the location of the port
    :param game_map: GameMap - the current map
    :param island_size: int - maximum steps for walking
    :param max_seeds: maximum number of paths that will be drunk-walked to create island chains
    :return: None - elevation map modified directly
    """
    num_seeds = randint(max_seeds // 2, max_seeds)
    seeds = get_seed_locations(width=game_map.width, height=game_map.height, num=num_seeds)
    height_map = [[0 for y in range(game_map.height)] for x in range(game_map.width)]
    
    for seed in seeds:
        size = randint(island_size // 2, island_size)
        x, y = seed
        cube_seed = hex_to_cube(Hex(column=x, row=y))
        for i in range(size):
            direction = randint(0, len(cube_directions))
            if direction == len(cube_directions):
                new_cube = cube_seed
            else:
                new_cube = cube_directions[direction]
            # make sure direction is not out of bounds (leaving a 1 tile margin around map)
            new_hex = cube_to_hex(new_cube)
            dx = new_hex.col
            dy = new_hex.row
            if game_map.in_bounds(x=x + dx, y=y + dy, margin=1):
                x = x + dx
                y = y + dy
                height_map[x][y] += 1
    
    islands = find_all_islands(height_map=height_map, width=game_map.width, height=game_map.height)
    largest, largest_islands = get_largest_islands(islands=islands)
    
    port_x = None
    port_y = None
    for island in islands:
        print(island)
        for tile in island:
            tile_x, tile_y = tile
            cube_tile = hex_to_cube(Hex(column=tile_x, row=tile_y))
            # surround each island tile with at least elevation 1
            for direction in cube_directions:
                new_hex = cube_to_hex(cube_add(cube_tile, direction))
                x = new_hex.col
                y = new_hex.row
                if game_map.in_bounds(x=x, y=y) and height_map[x][y] < Elevation.SHALLOWS.value:
                    height_map[x][y] = Elevation.SHALLOWS.value
        
        if len(island) == largest and not (port_x or port_y):
            valid_tiles = remove_bad_tiles(height_map, island)
            port_x, port_y = valid_tiles[randint(0, len(valid_tiles) - 1)]
            print(port_x, port_y)
    
    for x in range(game_map.width):
        for y in range(game_map.height):
            if height_map[x][y] > Elevation.VOLCANO.value:
                height_map[x][y] = Elevation.VOLCANO.value
            game_map.terrain[x][y] = Terrain(elevation=Elevation(height_map[x][y]))
            if x == port_x and y == port_y:
                game_map.terrain[port_x][port_y].decoration = Decoration('Port')


def remove_bad_tiles(height_map, island):
    """
    Used to remove tiles from an island coordinate list for placement of the Port (not on mountain or volcano),
    with at least 1 water neighbor TODO: this should probably be two so port not placed next to inaccessible "lake"
    :param height_map: elevation
    :param island: list of coordinates
    :return: list of valid coordinates a port can be placed on
    """
    choices = []
    for (x, y) in island:
        # make sure elevation is sand, grass, or jungle, and make sure there is at least 1 water next to tile
        if (Elevation.DUNES.value <= height_map[x][y] <= Elevation.JUNGLE.value) \
                and len(get_hex_land_neighbors(height_map, x, y)) < 6:  # not surrounded by 6 land tiles
            choices.append((x, y))
    return choices


def get_seed_locations(width: int, height: int, num: int):
    """
    Returns list of tile coordinate seeds for map generation
    :param width: int width of map
    :param height: int height of map
    :param num: int number of seed locations wanted
    :return: list of seed coordinates
    """
    seeds = []
    for i in range(num):
        x = randint(4, width - 5)
        y = randint(4, height - 5)
        seeds.append((x, y))
    return seeds


def get_largest_islands(islands):
    """
    Returns a list of the largest lists of connected tile coordinates, as well as that size
    :param islands: list of lists of coordinates (islands - connected land elevation tiles)
    :return: int size of the largest island,
             list of lists of the largest islands
    """
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
    """
    Returns a list of lists of tuple coordinates of adjacent "land" tiles (elevation > 2)
    :param height_map: list of lists of int "elevation" values
    :param width: width of the game map
    :param height: height of the game map
    :return: list of lists of coordinates
    """
    island_tiles = []  # holds set of all coordinates in island found so far
    explored = []
    island_list = []
    for x in range(1, width - 2):
        for y in range(1, height - 2):
            if (x, y) not in island_tiles and (x, y) not in explored and height_map[x][y] >= Elevation.DUNES.value:
                # found a land tile, so...
                #  get all tiles in this island
                new_island_tiles = explore_hex_island_iterative(height_map=height_map, x=x, y=y)
                explored.extend(new_island_tiles)
                island_list.append(new_island_tiles)
                # print(island_list)
    return island_list


def explore_hex_island_iterative(height_map, x, y):
    """
    Finds all "islands" on the game map. "islands" are sets of adjacent land tiles. "land tiles" have elevation > 2
    :param height_map: list of lists of int "elevation" values
    :param x: int x coordinate
    :param y: int y coordinate
    :return: list of tile coordinates
    """
    frontier = Queue()
    frontier.put((x, y))
    visited = [(x, y)]
    
    while not frontier.empty():
        current = frontier.get()
        x, y = current
        for neighbor in get_hex_land_neighbors(height_map=height_map, x=x, y=y):
            if neighbor not in visited:
                frontier.put(neighbor)
                visited.append(neighbor)
    return visited
