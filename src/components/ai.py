from random import randint

from src.components.mobile import can_move_direction
from src.map_objects.map_utils import get_hex_neighbors, hex_to_cube, Hex, get_spatial_relation, \
    cube_add, cube_direction, cube_to_hex
from src.death_functions import kill_player


class PeacefulMonster:
    def take_turn(self, game_map, player, message_log, colors, icons):
        entity = self.owner
        neighbors = get_hex_neighbors(entity.x, entity.y)
        if entity.mobile.current_speed < 1 \
                and can_move_direction(neighbors[entity.mobile.direction], game_map):
            entity.mobile.rowing = 1
            if (entity.x, entity.y) in player.view.fov:
                message_log.add_message("{} at {}:{} swims lazily".format(entity.name, entity.x, entity.y))
        else:
            direction = randint(-1, 1)
            entity.mobile.rotate(direction)
            if (entity.x, entity.y) in player.view.fov:
                message_log.add_message("{} at {}:{} wanders aimlessly".format(entity.name, entity.x, entity.y))
        return None


class MeleeMonster:  # SeaSerpent
    # TODO: find a way to implement last known location (last_seen) as a target hex - add state? need dijkstra maps
    def take_turn(self, game_map, target, message_log, colors, icons):
        state = None
        entity = self.owner
        neighbors = get_hex_neighbors(entity.x, entity.y)
        # critter can see target or has a target
        if (target.x, target.y) in entity.view.fov:
            # and hasattr(game_map.terrain[target.x][target.y], 'decoration') \
            # and game_map.terrain[target.x][target.y].decoration.name is not 'Port':
            # can see you
            message_log.add_message('The {} at {}:{} has spotted you!!'.format(entity.name, entity.x, entity.y),
                                    colors['light_red'])
            # in melee range
            if (target.x, target.y) in neighbors or (target.x, target.y) == (entity.x, entity.y):
                damage = 2
                message, result = target.fighter.take_damage(damage)
                message_log.add_message('The {} attacked your {} for {} damage!'.format(entity.name,
                                                                                        target.fighter.name,
                                                                                        damage), colors['light_red'])
                message_log.add_message(message)
                if result:  # entity is dead
                    message, state = kill_player(target, icons)
                message_log.add_message(message)
                return state
            
            # chase target
            else:
                expected_target_tile = Hex(target.x, target.y)
                target_dir = target.mobile.direction
                
                for step in range(0, target.mobile.current_speed):
                    expected_target_tile = cube_to_hex(
                        cube_add(hex_to_cube(expected_target_tile), cube_direction(target_dir)))
                
                (relative_location, relative_dir) = get_spatial_relation(expected_target_tile.col,
                                                                         expected_target_tile.row, target_dir, entity.x,
                                                                         entity.y, entity.mobile.direction)
                rl = 1  # rotate left / port
                rr = -1  # rotate right
                # action rules:
                if entity.mobile.current_speed < 1 \
                        and can_move_direction(neighbors[entity.mobile.direction], game_map):
                    entity.mobile.rowing = 2
                    message_log.add_message('{} has a burst of speed'.format(entity.name), colors['yellow'])
                elif relative_location in ["PH"] \
                        or relative_location in ["PBH", "PBA"] and relative_dir in [1, 2, 3, 4] \
                        or relative_location in ["PQA"] and relative_dir in [0, 1, 2, 3, 5] \
                        or relative_location in ["PQH"] and relative_dir in [0, 1, 2, 3] \
                        or relative_location in ["SQA"] and relative_dir in [2] \
                        or relative_location in ["SQH"] and relative_dir in [1, 2] \
                        or relative_location in ["FA", "AA"] and relative_dir in [1, 2]:
                    entity.mobile.rotate(rl)
                    message_log.add_message('{} turns to port'.format(entity.name))
                elif relative_location in ["SH"] \
                        or relative_location in ["PQA"] and relative_dir in [4] \
                        or relative_location in ["PQH"] and relative_dir in [4, 5] \
                        or relative_location in ["SBH", "SBA"] and relative_dir in [2, 3, 4, 5] \
                        or relative_location in ["SQA"] and relative_dir in [0, 1, 3, 4, 5] \
                        or relative_location in ["SQH"] and relative_dir in [0, 3, 4, 5] \
                        or relative_location in ["FA", "AA"] and relative_dir in [4, 5] \
                        or relative_location in ["AA"] and relative_dir in [3]:
                    entity.mobile.rotate(rr)
                    message_log.add_message('{} turns to starboard'.format(entity.name))
                elif relative_location in ["PBH", "PBA"] and relative_dir in [5] \
                        or relative_location in ["SBH", "SBA"] and relative_dir in [1] \
                        or relative_location in ["FA"] and relative_dir in [0, 3]:
                    entity.mobile.rowing = 2
                    message_log.add_message('{} has a burst of speed'.format(entity.name), colors['yellow'])
                elif relative_location in ["PBH", "PBA", "SBH", "SBA"] and relative_dir in [0]:
                    entity.mobile.rowing = 1
                    message_log.add_message('{} paces your vessel'.format(entity.name), colors['yellow'])
                elif relative_location in ["OO"] \
                        or relative_location in ["AA"] and relative_dir in [0]:
                    entity.mobile.rowing = -1
                    message_log.add_message('{} slows to wait for you'.format(entity.name), colors['yellow'])
        
        # critter can't see target - act like Peaceful Monster
        else:
            if entity.mobile.current_speed < 1 \
                    and can_move_direction(neighbors[entity.mobile.direction], game_map):
                entity.mobile.rowing = 1
                if (entity.x, entity.y) in target.view.fov:
                    message_log.add_message("{} at {}:{} swims lazily".format(entity.name, entity.x, entity.y))
            else:
                direction = randint(-1, 1)
                entity.mobile.rotate(direction)
                if (entity.x, entity.y) in target.view.fov:
                    message_log.add_message("{} at {}:{} wanders aimlessly".format(entity.name, entity.x, entity.y))
        
        return state
    

class BasicShip:
    def take_turn(self):
        print('The ' + self.owner.name + ' wonders when it will get to move.')
