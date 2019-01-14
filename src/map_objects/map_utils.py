from map_objects.tile import Elevation


class Cube:
    def __init__(self, x, y, z):
        """
        Container to hold cubic values in an (x, y, z) coordinate system
        :param x: int x value of an (x, y, z) coordinate system
        :param y: int y value of an (x, y, z) coordinate system
        :param z: int z value of an (x, y, z) coordinate system
        """
        self.x = x
        self.y = y
        self.z = z


class Hex:
    def __init__(self, column, row):
        """
        Container to hold a tile (x, y) coordinate
        :param column: int x value of an (x, y) coordinate system
        :param row: int y value of an (x, y) coordinate system
        """
        self.col = column
        self.row = row


"""
Returns the neighbor cube in the given direction
"""
cube_directions = [Cube(0, 1, -1),  # (0) Up
                   Cube(-1, 1, 0),  # (1) upper left
                   Cube(-1, 0, 1),  # (2) lower left
                   Cube(0, -1, 1),  # (3) Down
                   Cube(1, -1, 0),  # (4) lower right
                   Cube(1, 0, -1)]  # (5) upper right

"""
Returns the neighbor cube in the given direction DOES NOT ACCOUNT FOR OFFSET
"""
hex_directions = [(0, -1), (-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1)]

direction_angle = [0, 60, 120, 180, 240, 300]


def get_grid_from_coords(coords, player_coords, constants):
    """
    Returns x, y tile coordinates of the game map when given pixel coordinates in the view
    and the player's location (needed to center camera)
    :param coords: tuple (x, y) of pixel coordinate values
    :param player_coords: the player's (x, y) tile coordinate on the game map
    :param constants: dict containing map and tile sizes
    :return: corresponding (x, y) tile coordinate on the game map
    """
    x, y = coords
    player_col, player_row = player_coords
    col = player_col - 9 + (x - constants['map_width'] + constants['margin']) // constants['tile_size']
    row = player_row - 9 + (y - constants['half_tile'] * (col % 2)
                            + (player_col % 2) * constants['half_tile']
                            - constants['margin']) // constants['tile_size']
    return col, row


def get_hex_land_neighbors(height_map, x, y):
    """
    Returns neighboring land tiles of a given (x, y) map coordinate
    :param height_map: elevation grid of the neighboring hexes
    :param x: int x of the game map coordinate
    :param y: int y of the game map coordinate
    :return: list of tile coordinate (x, y) tuples
    """
    neighbors = []
    for direction in cube_directions:
        start_cube = hex_to_cube(hexagon=Hex(column=x, row=y))
        neighbor_hex = cube_to_hex(cube=cube_add(cube1=start_cube, cube2=direction))
        if height_map[neighbor_hex.col][neighbor_hex.row] >= Elevation.DUNES.value:
            neighbors.append((neighbor_hex.col, neighbor_hex.row))
    return neighbors


def get_hex_water_neighbors(height_map, x, y):
    """
    Returns neighboring water tiles of a given (x, y) map coordinate
    :param height_map: elevation grid of the neighboring hexes
    :param x: int x of the game map coordinate
    :param y: int y of the game map coordinate
    :return: list of tile coordinate (x, y) tuples
    """
    neighbors = []
    for direction in cube_directions:
        start_cube = hex_to_cube(hexagon=Hex(column=x, row=y))
        neighbor_hex = cube_to_hex(cube=cube_add(cube1=start_cube, cube2=direction))
        if height_map[neighbor_hex.col][neighbor_hex.row] < Elevation.DUNES.value:
            neighbors.append((neighbor_hex.col, neighbor_hex.row))
    return neighbors


def get_hex_neighbors(x, y):
    """
    Returns all neighboring tiles of a given (x, y) map coordinate
    :param x: int x of the game map coordinate
    :param y: int y of the game map coordinate
    :return: list of tile coordinate (x, y) tuples
    """
    neighbors = []
    for direction in cube_directions:
        start_cube = hex_to_cube(hexagon=Hex(column=x, row=y))
        neighbor_hex = cube_to_hex(cube=cube_add(cube1=start_cube, cube2=direction))
        neighbors.append((neighbor_hex.col, neighbor_hex.row))
    return neighbors


# Thanks Amit @redblobgames !!

def cube_to_hex(cube):
    """
    Convert cube coordinates to hexagonal (col, row) coordinates (directly translates to (x, y) map coordinates)
    :param cube: tile in cubic coordinates
    :return: tile in hexagonal coordinates
    """
    col = cube.x
    row = cube.z + (cube.x - cube.x % 2) // 2
    return Hex(col, row)


def hex_to_cube(hexagon):
    """
    Convert hexagonal (col, row) coordinates to cubic coordinates (easier to work with than (x, y) map coordinates)
    :param hexagon: tile in hexagonal coordinates
    :return: tile in cubic coordinates
    """
    x = hexagon.col
    z = hexagon.row - (hexagon.col - hexagon.col % 2) // 2
    y = -x - z
    return Cube(x, y, z)


def cube_distance(cube1, cube2):
    """
    Distance between two tiles in cubic coordinates
    :param cube1: origin cube
    :param cube2: target cube
    :return: int distance between cubes
    """
    return max(abs(cube1.x - cube2.x), abs(cube1.y - cube2.y), abs(cube1.z - cube2.z))


def offset_distance(hex1, hex2):
    cube1 = hex_to_cube(hexagon=hex1)
    cube2 = hex_to_cube(hexagon=hex2)
    return cube_distance(cube1=cube1, cube2=cube2)


def lerp(a, b, t):
    """
    cubic line drawing helper
    """
    return a + (b - a) * t


def cube_lerp(a, b, t):
    """
    cubic line drawing helper
    """
    return Cube(x=lerp(a.x, b.x, t), y=lerp(a.y, b.y, t), z=lerp(a.z, b.z, t))


def cube_line_draw(cube1, cube2):
    """
    function to return a list of cube coordinates in a line from cube1 to cube2
    :param cube1: starting cube coordinates
    :param cube2: ending cube coordinates
    :return: list of cubes from cube1 to cube2 inclusive
    """
    n = cube_distance(cube1=cube1, cube2=cube2)
    cube_line = []
    for i in range(0, n + 1):
        cube_line.append(cube_round(cube=cube_lerp(a=cube1, b=cube2, t=1.0 / n * i)))
    return cube_line[1:]


def cube_round(cube):
    """
    cubic line drawing helper
    """
    rx = round(cube.x)
    ry = round(cube.y)
    rz = round(cube.z)
    
    x_diff = abs(rx - cube.x)
    y_diff = abs(ry - cube.y)
    z_diff = abs(rz - cube.z)
    
    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry
    return Cube(rx, ry, rz)


def hex_round(hexagon):
    """
    cubic line drawing helper
    """
    return cube_to_hex(cube=cube_round(cube=hex_to_cube(hexagon=hexagon)))


def hex_line_draw(hex1: Hex, hex2: Hex):
    """
    Function to get a list of hexes forming a line between and including hex1 and hex2
    :param hex1: starting Hex coordinates
    :param hex2: ending Hex coordinates
    :return: list of Hexes forming the line
    """
    hex_line = []
    cube_line = cube_line_draw(cube1=hex_to_cube(hexagon=hex1), cube2=hex_to_cube(hexagon=hex2))
    for cube in cube_line:
        hex_line.append(cube_to_hex(cube=cube))
    return hex_line


def cube_direction(direction):
    """
    Returns neighboring cubic relational values in a given hex direction
    :param direction: int direction
    :return: cubic relational values of neighbor in given hex direction
    """
    return cube_directions[direction]


def cube_neighbor(cube, direction):
    """
    Returns neighboring cubic coordinates in a given hex direction
    :param cube: cubic coordinates
    :param direction: int direction
    :return: cubic coordinates of neighbor in the given direction
    """
    return cube_add(cube1=cube, cube2=cube_direction(direction))


def cube_add(cube1, cube2):
    """
    adds the cubic coordinate values of two cubes
    :param cube1: first cube
    :param cube2: second cube
    :return: cubic coordinates
    """
    return Cube(x=cube1.x + cube2.x, y=cube1.y + cube2.y, z=cube1.z + cube2.z)


def cube_rotate_cc(cube):
    """
    Returns cubic coordinates of a tile when rotated clockwise one direction
    :param cube: cube coords to rotate
    :return: rotated coordinates
    """
    new_x = - cube.z
    new_y = - cube.x
    new_z = - cube.y
    return Cube(x=new_x, y=new_y, z=new_z)


def get_fov(entity, game_map, game_time, game_weather, fog_view=0):
    """
    Returns the list of tiles that can be viewed by the given entity
    :param entity: given entity on the map
    :param game_map: the current GameMap (for terrain)
    :param game_time: current game Time (darkness effects view distance)
    :param game_weather: current map Weather (bad weather effects view distance)
    :param fog_view: int value of how many fog banks it takes to block line of sight
    :return: list of tiles in view
    """
    view = entity.view
    view += game_time.get_time_of_day_info['view']
    view += game_weather.get_weather_info['view']
    if entity.owner.wings:
        view += 1
    # account for phases of the moon
    if not (6 <= game_time.hrs < 18):
        if (13 < game_time.day < 18) \
                or (game_time.day == 13 and game_time.hrs >= 18) \
                or (game_time.day == 18 and game_time.hrs < 6):
            view -= 1
        elif (game_time.day > 28 or game_time.day < 3) \
                or (game_time.day == 28 and game_time.hrs >= 18) \
                or (game_time.day == 3 and game_time.hrs < 6):
            view += 1
    if view < 1:
        view = 1
    
    viewed_hexes = []
    center_coords = hex_to_cube(hexagon=Hex(column=entity.owner.x, row=entity.owner.y))
    viewed_hexes.append(Hex(column=entity.owner.x, row=entity.owner.y))
    current = center_coords
    
    for k in range(0, view):
        current = cube_neighbor(cube=current, direction=4)
    
    for i in range(0, 6):
        for j in range(0, view):
            cube_line = cube_line_draw(cube1=center_coords, cube2=current)
            fog = 0
            for cube in cube_line:
                hx = cube_to_hex(cube)
                if game_map.in_bounds(hx.col, hx.row) and game_map.fog[hx.col][hx.row]:
                    fog += 1
                if hx not in viewed_hexes[1:]:
                    viewed_hexes.append(hx)
                if game_map.in_bounds(hx.col, hx.row) \
                        and ((Elevation.SHALLOWS < game_map.terrain[hx.col][hx.row].elevation
                              and not entity.owner.wings)
                             or fog > fog_view):
                    break
            
            current = cube_neighbor(current, i)
    
    viewed = []
    for tile in viewed_hexes:
        if (0 <= tile.col < game_map.width) and (0 <= tile.row < game_map.height):
            viewed.append((tile.col, tile.row))
    view_set = set(viewed)
    
    return view_set


def get_target_hexes(player):
    """
    Returns target hexes for each weapon in an entities' weapon list
    :param player: attacking entity
    :return: list of tile coordinates
    """
    target_hexes = []
    p_cube = hex_to_cube(hexagon=Hex(column=player.x, row=player.y))
    if player.weapons and player.weapons.weapon_list:
        for weapon in player.weapons.weapon_list:
            if weapon.location == "Bow" and weapon.current_cd == 0:
                target_hexes.extend(get_axis_target_cubes(max_range=weapon.max_range,
                                                          p_cube=p_cube,
                                                          direction=player.mobile.direction))
            if weapon.location == "Stern" and weapon.current_cd == 0:
                target_hexes.extend(get_axis_target_cubes(max_range=weapon.max_range,
                                                          p_cube=p_cube,
                                                          direction=reverse_direction(direction=
                                                                                      player.mobile.direction)))
            if weapon.location == "Port" and weapon.current_cd == 0:
                target_hexes.extend(get_cone_target_cubes(max_range=weapon.max_range,
                                                          p_cube=p_cube,
                                                          p_direction=player.mobile.direction))
            if weapon.location == "Starboard" and weapon.current_cd == 0:
                target_hexes.extend(get_cone_target_cubes(max_range=weapon.max_range,
                                                          p_cube=p_cube,
                                                          p_direction=reverse_direction(direction=
                                                                                        player.mobile.direction)))
    return target_hexes


def get_target_hexes_at_location(player, location, max_range):
    """
    Returns list of tile coordinates that can be targeted from a given facing the weapon list
    :param player: attacking entity
    :param location: string name of the facing of the weapon
    :param max_range: int distance the weapon can shoot
    :return: list of tile coordinates
    """
    target_hexes = []
    p_cube = hex_to_cube(hexagon=Hex(column=player.x, row=player.y))
    if location == "Bow":
        target_hexes.extend(get_axis_target_cubes(max_range=max_range,
                                                  p_cube=p_cube,
                                                  direction=player.mobile.direction))
    if location == "Stern":
        target_hexes.extend(get_axis_target_cubes(max_range=max_range,
                                                  p_cube=p_cube,
                                                  direction=reverse_direction(direction=player.mobile.direction)))
    if location == "Port":
        target_hexes.extend(get_cone_target_cubes(max_range=max_range,
                                                  p_cube=p_cube,
                                                  p_direction=player.mobile.direction))
    if location == "Starboard":
        target_hexes.extend(get_cone_target_cubes(max_range=max_range,
                                                  p_cube=p_cube,
                                                  p_direction=reverse_direction(direction=player.mobile.direction)))
    return target_hexes


def reverse_direction(direction):
    """
    Returns value of the opposite direction
    :param direction: int current direction
    :return: int opposite direction
    """
    new_direction = direction - 3
    if new_direction < 0:
        return new_direction + 6
    else:
        return new_direction


def get_axis_target_cubes(max_range, p_cube, direction):
    """
    Returns a list of tile coordinates on a given direction's axis
    :param max_range: int maximum distance a weapon can shoot
    :param p_cube: cubic coordinates of attacker
    :param direction: int attacker's facing
    :return: list of tile coordinates
    """
    target_hexes = []
    current_cube = p_cube
    for r in range(max_range):
        tile = cube_to_hex(cube=cube_add(cube1=current_cube, cube2=cube_directions[direction]))
        target_hexes.append((tile.col, tile.row))
        current_cube = hex_to_cube(hexagon=tile)
    return target_hexes


def get_cone_target_cubes(max_range, p_cube, p_direction):
    """
    Returns a list of tile coordinates between a given direction's two axes
    :param max_range: int maximum distance a weapon can shoot
    :param p_cube: cubic coordinates of attacker
    :param p_direction: int attacker's facing
    :return: list of tile coordinates
    """
    # this assumes direction 0, location x0 y0 z0
    target_cubes = []
    for x in range(1, max_range + 1):
        for y in range(0, x + 1):
            target_cubes.append(Cube(x=-x, y=y, z=x - y))
    # rotate and translate, then convert to (x, y)
    target_hexes = []
    for cube in target_cubes:
        r_cube = cube
        for step in range(6 - p_direction):
            r_cube = cube_rotate_cc(cube=r_cube)
        t_cube = cube_add(cube1=p_cube, cube2=r_cube)
        t_hex = cube_to_hex(cube=t_cube)
        target_hexes.append((t_hex.col, t_hex.row))
    return target_hexes


def get_spatial_relation(tx, ty, td, ex, ey, ed):
    """
    Used to determine the and relative location and direction of travel between two entities
    :param tx: int x coordinate of target
    :param ty: int y coordinate of target
    :param td: int directional facing of target
    :param ex: int x coordinate of entity
    :param ey: int y coordinate of entity
    :param ed: int directional facing of entity
    :return: spatial relation between entity and target:
        P: port
        S: starboard
        F: fore
        A: aft
        
        B: Bow (ahead)
        Q: quarter (behind)
        
        H: hexes between axes
        A: axis
        
        OO: on top of
    """
    target_cube = hex_to_cube(Hex(column=tx, row=ty))
    entity_cube = hex_to_cube(Hex(column=ex, row=ey))
    
    target_rotated = Cube(x=target_cube.x - entity_cube.x,
                          y=target_cube.y - entity_cube.y,
                          z=target_cube.z - entity_cube.z)
    rotated_direction = td
    # do rotation
    
    for step in range(ed):
        target_rotated = cube_rotate_cc(cube=target_rotated)
        rotated_direction -= 1
    if rotated_direction < 0:
        rotated_direction += 6
    # print("relative direction: ", rotated_direction)
    target_rotated = cube_add(cube1=target_rotated, cube2=entity_cube)
    
    # find relationship
    if (entity_cube.x - target_rotated.x) > 0 and (entity_cube.y - target_rotated.y) > 0:
        # print("target was in Port Quarter hextant, relative direction: {}".format(rotated_direction))
        return "PQH", rotated_direction
    elif (entity_cube.x - target_rotated.x) < 0 and (entity_cube.y - target_rotated.y) < 0:
        # print("target was in Starboard Bow hextant, relative direction: {}".format(rotated_direction))
        return "SBH", rotated_direction
    elif (entity_cube.x - target_rotated.x) > 0 and (entity_cube.z - target_rotated.z) > 0:
        # print("target was in Port Bow hextant, relative direction: {}".format(rotated_direction))
        return "PBH", rotated_direction
    elif (entity_cube.x - target_rotated.x) < 0 and (entity_cube.z - target_rotated.z) < 0:
        # print("target was in Starboard Quarter hextant, relative direction: {}".format(rotated_direction))
        return "SQH", rotated_direction
    elif (entity_cube.y - target_rotated.y) > 0 and (entity_cube.z - target_rotated.z) > 0:
        # print("target was in Starboard hextant, relative direction: {}".format(rotated_direction))
        return "SH", rotated_direction
    elif (entity_cube.y - target_rotated.y) < 0 and (entity_cube.z - target_rotated.z) < 0:
        # print("target was in Port hextant, relative direction: {}".format(rotated_direction))
        return "PH", rotated_direction
    elif (entity_cube.x - target_rotated.x) > 0 > (entity_cube.y - target_rotated.y) \
            and (entity_cube.z - target_rotated.z) == 0:
        # print("target was on Port Bow axis, relative direction: {}".format(rotated_direction))
        return "PBA", rotated_direction
    elif (entity_cube.x - target_rotated.x) < 0 < (entity_cube.y - target_rotated.y) \
            and (entity_cube.z - target_rotated.z) == 0:
        # print("target was on Starboard Quarter axis, relative direction: {}".format(rotated_direction))
        return "SQA", rotated_direction
    elif (entity_cube.x - target_rotated.x) > 0 > (entity_cube.z - target_rotated.z) \
            and ((entity_cube.y - target_rotated.y) == 0):
        # print("target was on Port Quarter axis, relative direction: {}".format(rotated_direction))
        return "PQA", rotated_direction
    elif (entity_cube.x - target_rotated.x) < 0 < (entity_cube.z - target_rotated.z) \
            and ((entity_cube.y - target_rotated.y) == 0):
        # print("target was on Starboard Bow axis, relative direction: {}".format(rotated_direction))
        return "SBA", rotated_direction
    elif (entity_cube.y - target_rotated.y) > 0 > (entity_cube.z - target_rotated.z) \
            and ((entity_cube.x - target_rotated.x) == 0):
        # print("target was directly Astern, relative direction: {}".format(rotated_direction))
        return "AA", rotated_direction
    elif (entity_cube.y - target_rotated.y) < 0 < (entity_cube.z - target_rotated.z) \
            and ((entity_cube.x - target_rotated.x) == 0):
        # print("target was directly Forward, relative direction: {}".format(rotated_direction))
        return "FA", rotated_direction
    else:  # expected position of target is on entity's expected location
        return "OO", rotated_direction
