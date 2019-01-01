from src.map_objects.tile import Elevation


class Cube:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Hex:
    def __init__(self, column, row):
        self.col = column
        self.row = row


#                  Up (0)          upper left (1)  lower left (2)  Down (3)        lower right (4) upper right (5)
cube_directions = [Cube(0, 1, -1), Cube(-1, 1, 0), Cube(-1, 0, 1), Cube(0, -1, 1), Cube(1, -1, 0), Cube(1, 0, -1)]

hex_directions = [(0, -1), (-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1)]

direction_angle = [0, 60, 120, 180, 240, 300]


# compass_direction = {
#     "N": 0,
#     "NW": 1,
#     "SW": 2,
#     "S": 3,
#     "SE": 4,
#     "NE": 5
# }


def get_grid_from_coords(coords, player_coords, constants):
    x, y = coords
    player_col, player_row = player_coords
    col = player_col - 9 + (x - constants['map_width'] + constants['margin']) // constants['tile_size']
    row = player_row - 9 + (y - constants['half_tile'] * (col % 2)
                            + (player_col % 2) * constants['half_tile'] - constants['margin']) // constants['tile_size']
    return col, row


def get_hex_land_neighbors(height_map, x, y):
    neighbors = []
    for direction in hex_directions:
        dx, dy = direction
        if height_map[dx + x][dy + y + (x % 2) * (dx % 2)] >= Elevation.DUNES.value:
            neighbors.append((dx + x, dy + y + (x % 2) * (dx % 2)))
    return neighbors


def get_hex_water_neighbors(height_map, x, y):
    neighbors = []
    for direction in hex_directions:
        dx, dy = direction
        if height_map[dx + x][dy + y + (x % 2) * (dx % 2)] < Elevation.DUNES.value:
            neighbors.append((dx + x, dy + y + (x % 2) * (dx % 2)))
    return neighbors


def get_hex_neighbors(x, y):
    neighbors = []
    for direction in hex_directions:
        dx, dy = direction
        neighbors.append((dx + x, dy + y + (x % 2) * (dx % 2)))
    return neighbors


# Thanks Amit @redblobgames !!

def cube_to_hex(cube):
    col = cube.x
    row = cube.z + (cube.x - cube.x % 2) // 2
    return Hex(col, row)


def hex_to_cube(hexagon):
    x = hexagon.col
    z = hexagon.row - (hexagon.col - hexagon.col % 2) // 2
    y = -x - z
    return Cube(x, y, z)


def cube_distance(cube1, cube2):
    return max(abs(cube1.x - cube2.x), abs(cube1.y - cube2.y), abs(cube1.z - cube2.z))


def offset_distance(hex1, hex2):
    cube1 = hex_to_cube(hex1)
    cube2 = hex_to_cube(hex2)
    return cube_distance(cube1, cube2)


def lerp(a, b, t):
    return a + (b - a) * t


def cube_lerp(a, b, t):
    return Cube(lerp(a.x, b.x, t), lerp(a.y, b.y, t), lerp(a.z, b.z, t))


def cube_line_draw(cube1, cube2):
    """
    function to return a list of cube coordinates in a line from cube1 to cube2
    :param cube1: starting cube coordinates
    :param cube2: ending cube coordinates
    :return: list of cubes from cube1 to cube2 inclusive
    """
    n = cube_distance(cube1, cube2)
    cube_line = []
    for i in range(0, n + 1):
        cube_line.append(cube_round(cube_lerp(cube1, cube2, 1.0 / n * i)))
    return cube_line[1:]


def cube_round(cube):
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
    return cube_to_hex(cube_round(hex_to_cube(hexagon)))


def hex_line_draw(hex1: Hex, hex2: Hex):
    """
    Function to get a list of hexes forming a line between and including hex1 and hex2
    :param hex1: starting Hex coordinates
    :param hex2: ending Hex coordinates
    :return: list of Hexes forming the line
    """
    hex_line = []
    cube_line = cube_line_draw(hex_to_cube(hex1), hex_to_cube(hex2))
    for cube in cube_line:
        hex_line.append(cube_to_hex(cube))
    return hex_line


def cube_direction(direction):
    return cube_directions[direction]


def cube_neighbor(cube, direction):
    return cube_add(cube, cube_direction(direction))


def cube_add(cube1, cube2):
    return Cube(cube1.x + cube2.x, cube1.y + cube2.y, cube1.z + cube2.z)


def cube_rotate_cc(cube):
    new_x = - cube.z
    new_y = - cube.x
    new_z = - cube.y
    return Cube(new_x, new_y, new_z)


def get_fov(fighter, game_map):
    view = fighter.view
    if fighter.owner.wings:
        view += 1
    viewed_hexes = []
    center_coords = hex_to_cube(Hex(fighter.owner.x, fighter.owner.y))
    viewed_hexes.append(Hex(fighter.owner.x, fighter.owner.y))
    current = center_coords
    
    for k in range(0, view):
        current = cube_neighbor(current, 4)
    
    for i in range(0, 6):
        for j in range(0, view):
            cube_line = cube_line_draw(center_coords, current)
            fog = 0
            for cube in cube_line:
                hx = cube_to_hex(cube)
                if game_map.in_bounds(hx.col, hx.row) and game_map.fog[hx.col][hx.row]:
                    fog += 1
                if hx not in viewed_hexes[1:]:
                    viewed_hexes.append(hx)
                if game_map.in_bounds(hx.col, hx.row) \
                        and (Elevation.SHALLOWS < game_map.terrain[hx.col][hx.row].elevation or fog > 0):
                    break
            
            current = cube_neighbor(current, i)
    
    viewed = []
    for tile in viewed_hexes:
        if (0 <= tile.col < game_map.width) and (0 <= tile.row < game_map.height):
            viewed.append((tile.col, tile.row))
    view_set = set(viewed)
    
    return view_set


def get_cell_from_mouse(x, y, player_column, player_row):
    col = player_column - 9 + (x - 200) // 32
    row = player_row - 9 + (y - 16 * (col % 2) + (player_column % 2) * 16) // 32
    # print('x:{} y:{} column:{} row:{}'.format(x, y, col, row))
    return col, row


def get_target_hexes(player):
    target_hexes = []
    p_cube = hex_to_cube(Hex(player.x, player.y))
    if player.weapons and player.weapons.weapon_list:
        for weapon in player.weapons.weapon_list:
            if weapon.location == "Bow" and weapon.current_cd == 0:
                target_hexes.extend(get_axis_target_cubes(weapon.max_range, p_cube,
                                                          player.mobile.direction))
            if weapon.location == "Stern" and weapon.current_cd == 0:
                target_hexes.extend(get_axis_target_cubes(weapon.max_range, p_cube,
                                                          reverse_direction(player.mobile.direction)))
            if weapon.location == "Port" and weapon.current_cd == 0:
                target_hexes.extend(get_cone_target_cubes(weapon.max_range, p_cube,
                                                          player.mobile.direction))
            if weapon.location == "Starboard" and weapon.current_cd == 0:
                target_hexes.extend(get_cone_target_cubes(weapon.max_range, p_cube,
                                                          reverse_direction(player.mobile.direction)))
    return target_hexes


def get_target_hexes_at_location(player, location, max_range):
    target_hexes = []
    p_cube = hex_to_cube(Hex(player.x, player.y))
    if location == "Bow":
        target_hexes.extend(get_axis_target_cubes(max_range, p_cube, player.mobile.direction))
    if location == "Stern":
        target_hexes.extend(get_axis_target_cubes(max_range, p_cube, reverse_direction(player.mobile.direction)))
    if location == "Port":
        target_hexes.extend(get_cone_target_cubes(max_range, p_cube, player.mobile.direction))
    if location == "Starboard":
        target_hexes.extend(get_cone_target_cubes(max_range, p_cube, reverse_direction(player.mobile.direction)))
    return target_hexes


def reverse_direction(direction):
    new_direction = direction - 3
    if new_direction < 0:
        return new_direction + 6
    else:
        return new_direction


def get_axis_target_cubes(max_range, p_cube, direction):
    target_hexes = []
    current_cube = p_cube
    for r in range(max_range):
        tile = cube_to_hex(cube_add(current_cube, cube_directions[direction]))
        target_hexes.append((tile.col, tile.row))
        current_cube = hex_to_cube(tile)
    return target_hexes


def get_cone_target_cubes(max_range, p_cube, p_direction):
    # this assumes direction 0, location x0 y0 z0
    target_cubes = []
    for x in range(1, max_range + 1):
        for y in range(0, x + 1):
            target_cubes.append(Cube(-x, y, x - y))
    # rotate and translate, then convert to (x, y)
    target_hexes = []
    for cube in target_cubes:
        r_cube = cube
        for step in range(6 - p_direction):
            r_cube = cube_rotate_cc(r_cube)
        t_cube = cube_add(p_cube, r_cube)
        t_hex = cube_to_hex(t_cube)
        target_hexes.append((t_hex.col, t_hex.row))
    return target_hexes


def get_spatial_relation(tx, ty, td, ex, ey, ed):
    target_cube = hex_to_cube(Hex(tx, ty))
    entity_cube = hex_to_cube(Hex(ex, ey))
    
    target_rotated = Cube(target_cube.x - entity_cube.x, target_cube.y - entity_cube.y, target_cube.z - entity_cube.z)
    rotated_direction = td
    # do rotation
    
    for step in range(ed):
        target_rotated = cube_rotate_cc(target_rotated)
        rotated_direction -= 1
    if rotated_direction < 0:
        rotated_direction += 6
    # print("relative direction: ", rotated_direction)
    target_rotated = cube_add(target_rotated, entity_cube)
    
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
