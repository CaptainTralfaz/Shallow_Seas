from random import randint

from components.mobile import can_move_direction
from death_functions import kill_player
from map_objects.map_utils import get_hex_neighbors, hex_to_cube, Hex, get_spatial_relation, \
    cube_add, cube_direction, cube_to_hex


class PeacefulMonster:
    """
    A peaceful entity that wanders the map randomly
    """
    def take_turn(self, game_map, target, message_log, colors, icons):
        entity = self.owner
        neighbors = get_hex_neighbors(x=entity.x, y=entity.y)
        if entity.mobile.current_speed < 1 \
                and can_move_direction(entity=entity, neighbor=neighbors[entity.mobile.direction], game_map=game_map):
            entity.mobile.rowing = 1
            if (entity.x, entity.y) in target.view.fov:
                message_log.add_message(message="{} at {}:{} swims lazily".format(entity.name, entity.x, entity.y))
        else:
            direction = randint(-1, 1)
            entity.mobile.rotate(direction)
            if (entity.x, entity.y) in target.view.fov:
                message_log.add_message(message="{} at {}:{} wanders aimlessly".format(entity.name, entity.x, entity.y))
        return None


class ScaredyCat:
    """
    An entity that runs away from the player
    """


class MeleeMonster:  # Sea Serpent and Giant Bat
    """
    An entity that tries to get next to the player to attack
    """
    # TODO: find a way to implement last known location (last_seen) as a target hex - add state? need dijkstra maps
    def take_turn(self, game_map, target, message_log, colors, icons):
        state = None
        entity = self.owner
        neighbors = get_hex_neighbors(x=entity.x, y=entity.y)
        # critter can see target or has a target
        if (target.x, target.y) in entity.view.fov:
            # can see you
            message_log.add_message('The {} at {}:{} has spotted you!!'.format(entity.name, entity.x, entity.y),
                                    colors['light_red'])
            # in melee range
            if (target.x, target.y) in neighbors or (target.x, target.y) == (entity.x, entity.y):
                damage = entity.size.value + 1
                death_result = False
                details = []
                if entity.name == 'Giant Bat':
                    hit_zone = randint(0, 10)
                    if hit_zone < 5 and target.mast_sail.max_sails > 0:  # and target.mast_sail.current_sails > 0:
                        death_result, details = target.mast_sail.take_sail_damage(amount=damage)
                        message_log.unpack(details=details, color=colors['amber'])
                    else:
                        death_result, details = target.crew.take_damage(amount=damage)
                        message_log.unpack(details=details, color=colors['amber'])
                elif entity.name == 'Sea Serpent':
                    death_result, details = target.fighter.take_damage(amount=damage)
                    message_log.unpack(details=details, color=colors['amber'])
                
                if death_result:  # entity is dead
                    message, state = kill_player(player=target, icons=icons)
                    message_log.add_message(message=message, color=colors['red'])
                return state
            
            # chase target
            else:
                expected_target_tile = Hex(column=target.x, row=target.y)
                target_dir = target.mobile.direction
                
                for step in range(0, target.mobile.current_speed):
                    expected_target_tile = cube_to_hex(cube=cube_add(cube1=hex_to_cube(hexagon=expected_target_tile),
                                                                     cube2=cube_direction(direction=target_dir)))
                
                (relative_location, relative_dir) = get_spatial_relation(tx=expected_target_tile.col,
                                                                         ty=expected_target_tile.row,
                                                                         td=target_dir,
                                                                         ex=entity.x,
                                                                         ey=entity.y,
                                                                         ed=entity.mobile.direction)
                rl = 1  # rotate left / port
                rr = -1  # rotate right
                # action rules:
                if entity.mobile.current_speed < 1 \
                        and can_move_direction(entity=entity,
                                               neighbor=neighbors[entity.mobile.direction],
                                               game_map=game_map):
                    entity.mobile.rowing = 2
                    message_log.add_message(message='{} has a burst of speed'.format(entity.name),
                                            color=colors['yellow'])
                elif relative_location in ["PH"] \
                        or relative_location in ["PBH", "PBA"] and relative_dir in [1, 2, 3, 4] \
                        or relative_location in ["PQA"] and relative_dir in [0, 1, 2, 3, 5] \
                        or relative_location in ["PQH"] and relative_dir in [0, 1, 2, 3] \
                        or relative_location in ["SQA"] and relative_dir in [2] \
                        or relative_location in ["SQH"] and relative_dir in [1, 2] \
                        or relative_location in ["FA", "AA"] and relative_dir in [1, 2]:
                    entity.mobile.rotate(rotate=rl)
                    message_log.add_message(message='{} turns to port'.format(entity.name))
                elif relative_location in ["SH"] \
                        or relative_location in ["PQA"] and relative_dir in [4] \
                        or relative_location in ["PQH"] and relative_dir in [4, 5] \
                        or relative_location in ["SBH", "SBA"] and relative_dir in [2, 3, 4, 5] \
                        or relative_location in ["SQA"] and relative_dir in [0, 1, 3, 4, 5] \
                        or relative_location in ["SQH"] and relative_dir in [0, 3, 4, 5] \
                        or relative_location in ["FA", "AA"] and relative_dir in [4, 5] \
                        or relative_location in ["AA"] and relative_dir in [3]:
                    entity.mobile.rotate(rotate=rr)
                    message_log.add_message(message='{} turns to starboard'.format(entity.name))
                elif relative_location in ["PBH", "PBA"] and relative_dir in [5] \
                        or relative_location in ["SBH", "SBA"] and relative_dir in [1] \
                        or relative_location in ["FA"] and relative_dir in [0, 3]:
                    entity.mobile.rowing = 2
                    message_log.add_message(message='{} has a burst of speed'.format(entity.name),
                                            color=colors['yellow'])
                elif relative_location in ["PBH", "PBA", "SBH", "SBA"] and relative_dir in [0]:
                    entity.mobile.rowing = 1
                    message_log.add_message(message='{} paces your vessel'.format(entity.name),
                                            color=colors['yellow'])
                elif relative_location in ["OO"] \
                        or relative_location in ["AA"] and relative_dir in [0]:
                    entity.mobile.rowing = -1
                    message_log.add_message(message='{} slows to wait for you'.format(entity.name),
                                            color=colors['yellow'])
        
        # critter can't see target - act like Peaceful Monster
        else:
            if entity.mobile.current_speed < 1 \
                    and can_move_direction(entity=entity,
                                           neighbor=neighbors[entity.mobile.direction],
                                           game_map=game_map):
                entity.mobile.rowing = 1
                if (entity.x, entity.y) in target.view.fov:
                    message_log.add_message(message="{} at {}:{} swims lazily".format(entity.name,
                                                                                      entity.x, entity.y))
            else:
                direction = randint(-1, 1)
                entity.mobile.rotate(direction)
                if (entity.x, entity.y) in target.view.fov:
                    message_log.add_message(message="{} at {}:{} wanders aimlessly".format(entity.name,
                                                                                           entity.x, entity.y))
        
        return state


class BasicShip:
    def take_turn(self):
        print('The ' + self.owner.name + ' wonders when it will get to move.')
