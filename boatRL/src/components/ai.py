from random import randint

from src.components.mobile import can_move_direction
from src.map_objects.map_utils import get_hex_neighbors, hex_to_cube, Hex, get_spatial_relation, \
    cube_add, cube_direction, cube_to_hex


class PeacefulMonster:
    def take_turn(self, game_map, player):
        entity = self.owner
        neighbors = get_hex_neighbors(entity.x, entity.y)
        if entity.mobile.current_speed < 1 \
                and can_move_direction(neighbors[entity.mobile.direction], game_map):
            entity.mobile.rowing = 1
        
        else:
            direction = randint(-1, 1)
            entity.mobile.rotate(direction)


class MeleeMonster:
    # TODO: find a way to implement last known location (last_seen) as a target hex
    def take_turn(self, game_map, target):
        messages = []
        entity = self.owner
        neighbors = get_hex_neighbors(entity.x, entity.y)
        # critter can see target or has a target
        if (target.x, target.y) in entity.view.fov and (target.x, target.y) not in game_map.towns:
            # can see you
            messages.append({'message': 'The {} at {}:{} has spotted you'.format(entity.name, entity.x, entity.y)})
            # in melee range
            if (target.x, target.y) in get_hex_neighbors(entity.x, entity.y) \
                    or (target.x, target.y) == (entity.x, entity.y):
                
                print("The {} attacked your ship!!".format(entity.name))
            # chase target
            else:
                expected_tile = Hex(target.x, target.y)
                expected_dir = target.mobile.direction
                
                for step in range(target.mobile.current_speed):
                    expected_tile = cube_to_hex(cube_add(hex_to_cube(expected_tile),
                                                         cube_direction(expected_dir)))
                # print(target.x, target.y, expected_tile.col, expected_tile.row)
                
                relative_location, relative_dir = get_spatial_relation(expected_tile.col,
                                                                       expected_tile.row,
                                                                       target.mobile.direction,
                                                                       entity.x,
                                                                       entity.y,
                                                                       entity.mobile.direction)
                rl = 1  # rotate left
                rr = -1  # rotate right
                # action rules:
                if entity.mobile.current_speed < 1 \
                        and can_move_direction(neighbors[entity.mobile.direction], game_map):
                    entity.mobile.rowing = 2  # messages.append({'rowing': 2})
                elif relative_location in ["PH"] \
                        or relative_location in ["PBH", "PBA"] and relative_dir in [0, 1, 2, 3, 4] \
                        or relative_location in ["PQA"] and relative_dir in [0, 1, 2, 3, 5] \
                        or relative_location in ["PQH"] and relative_dir in [0, 1, 2, 3] \
                        or relative_location in ["SQA"] and relative_dir in [2] \
                        or relative_location in ["SQH"] and relative_dir in [1, 2] \
                        or relative_location in ["FA", "AA"] and relative_dir in [1, 2]:
                    entity.mobile.rotate(rl)  # messages.append({'rotate': rl})
                elif relative_location in ["SH"] \
                        or relative_location in ["PQA"] and relative_dir in [4] \
                        or relative_location in ["PQH"] and relative_dir in [4, 5] \
                        or relative_location in ["SBH", "SBA"] and relative_dir in [0, 2, 3, 4, 5] \
                        or relative_location in ["SQA"] and relative_dir in [0, 1, 3, 4, 5] \
                        or relative_location in ["SQH"] and relative_dir in [0, 3, 4, 5] \
                        or relative_location in ["FA", "AA"] and relative_dir in [4, 5] \
                        or relative_location in ["AA"] and relative_dir in [3]:
                    entity.mobile.rotate(rr)  # messages.append({'rotate': rr})
                elif relative_location in ["PBH", "PBA"] and relative_dir in [5] \
                        or relative_location in ["SBH", "SBA"] and relative_dir in [1] \
                        or relative_location in ["FA"] and relative_dir in [0, 3]:
                    entity.mobile.rowing = 2  # messages.append({'rowing': 2})
                elif relative_location in ["AA"] and relative_dir in [0]:
                    entity.mobile.rowing = -1  # messages.append({'rowing': -1})
        
        # critter can't see target - act like Peaceful Monster
        else:
            if entity.mobile.current_speed < 1 \
                    and can_move_direction(neighbors[entity.mobile.direction], game_map):
                entity.mobile.rowing = 1  # messages.append({'rowing': 1})
            else:
                direction = randint(-1, 1)
                entity.mobile.rotate(direction)  # messages.append({'rotate': direction})
        
        return messages

class BasicShip:
    def take_turn(self):
        print('The ' + self.owner.name + ' wonders when it will get to move.')
