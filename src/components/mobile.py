from src.map_objects.map_utils import hex_directions
from src.map_objects.tile import Elevation
from src.death_functions import kill_player, kill_monster


class Mobile:
    def __init__(self, direction, max_momentum, max_speed=2, speed=0):
        """
        Component detailing movement for Entities that can do so
        :param direction: int direction Entity will travel (aka facing)
        :param max_momentum: int maximum size of momentum that can be built up before speed change
        :param max_speed: int maximum number of tiles an Entity can travel in a turn
        :param speed: int current number of tiles an Entity will travel each turn
        """
        self.direction = direction
        self.max_momentum = max_momentum
        self.current_momentum = self.max_momentum
        self.max_speed = max_speed
        self.current_speed = speed
        self.rowing = False
        self.catching_wind = False
    
    def move(self, game_map, player, icons):
        """
        Change tile coordinates in a line (determined by speed and direction of travel)
        :param game_map: current game map
        :param player: player entity
        :param icons: for death functions
        :return: None
        """
        # Move the entity by their current_speed
        death_state = None
        results = []
        dx, dy = hex_directions[self.direction]
        for speed in range(0, self.current_speed):
            new_x = self.owner.x + dx
            if dx == 0:
                new_y = self.owner.y + dy
            else:
                new_y = self.owner.y + dy + self.owner.x % 2
            # check for collisions!
            # TODO: Send to collision method ?, (as determined by movement type: sail, flying, swim/row, etc)
            if game_map.in_bounds(new_x, new_y) \
                    and game_map.terrain[new_x][new_y].decoration \
                    and game_map.terrain[new_x][new_y].decoration.name == 'Port' \
                    and self.owner.name is "player":
                results.append('{} sailed into Port'.format(self.owner.name))
                self.owner.x = new_x
                self.owner.y = new_y
                self.current_speed = 0
                self.current_momentum = 0
                if self.owner.mast_sail:
                    self.owner.mast_sail.current_sails = 0
                break
            elif game_map.in_bounds(x=new_x, y=new_y) and \
                    game_map.terrain[new_x][new_y].elevation > Elevation.SHALLOWS \
                    and not self.owner.wings:
                if (self.owner.x, self.owner.y) in player.view.fov:
                    message = "{} crashed into island".format(self.owner.name)
                    if self.owner.fighter:
                        death_result, details = self.owner.fighter.take_damage(self.current_speed)
                                                                               # * self.owner.size.value)
                        message += (' and takes {} {} damage!'.format(self.owner.name,
                                                                      self.current_speed,  # * self.owner.size.value,
                                                                      self.owner.fighter.name))
                        if death_result:
                            if self.owner.name == 'player':
                                death_message, death_state = kill_player(player=player, icons=icons)
                                results.append(death_message)
                            else:
                                kill_monster(entity=self.owner, icons=icons)
                    else:
                        message += '!'
                    results.append(message)
                    results.append('{} speed reduced to 0'.format(self.owner.name))
                self.current_speed = 0
                self.current_momentum = self.max_momentum
                break
            else:
                # Just move
                self.owner.x = new_x
                self.owner.y = new_y
        return results, death_state
    
    def rotate(self, rotate: int):
        """
        Change directional facing of an Entity
        :param rotate: int (1) rotate Port (-1) rotate starboard
        :return: Message for message log
        """
        results = ['{} rotates to {}'.format(self.owner.name, 'port' if rotate == 1 else 'starboard')]
        self.direction += rotate
        if self.direction > len(hex_directions) - 1:
            self.direction -= len(hex_directions)
        elif self.direction < 0:
            self.direction += len(hex_directions)
        return results
    
    def increase_momentum(self, amount: int, reason: str):
        """
        Modify current momentum of an Entity, and speed if necessary
        :param amount: int amount modify momentum
        :param reason: str reason for messages
        :return: None - eventually messages
        """
        results = []
        if reason == 'wind':
            if self.current_momentum + amount > self.max_momentum and self.current_speed == self.max_speed:
                if self.current_momentum == self.max_momentum:
                    results.append('{} maintains top speed'.format(self.owner.name))
                else:
                    self.current_momentum = self.max_momentum
                    results.append('{} reached top speed'.format(self.owner.name))
            elif self.current_momentum + amount > self.max_momentum and self.current_speed < self.max_speed:
                self.current_momentum += (amount - 1 - self.max_momentum)
                self.current_speed += 1
                results.append('{} gains speed from {}'.format(self.owner.name, reason))
            else:
                self.current_momentum += amount
        else:
            if self.current_speed > 0:
                if self.current_momentum + amount > self.max_momentum:
                    self.current_momentum = self.max_momentum
                    results.append('{} maintains speed from {}'.format(self.owner.name, reason))
                else:
                    self.current_momentum += amount
            elif self.current_momentum + amount > self.max_momentum:
                self.current_speed += 1
                self.current_momentum += (amount - 1 - self.max_momentum)
                results.append('{} gains speed from {}'.format(self.owner.name, reason))
            else:
                self.current_momentum += amount
        return results
    
    def decrease_momentum(self, amount: int, reason: str):
        """
        Decrease current momentum of an Entity, and speed if necessary
        :param amount: int amount modify momentum
        :param reason: str reason for messages
        :return: None - eventually messages
        """
        results = []
        if self.current_speed == 0:
            if self.current_momentum == 0:
                results.append('{} remains stopped'.format(self.owner.name))
            elif self.current_momentum + amount <= 0:
                self.current_momentum = 0
                results.append('{} stops due to {}'.format(self.owner.name, reason))
            else:
                self.current_momentum += amount
        else:
            self.current_momentum += amount
            if self.current_momentum < 0:
                self.current_momentum += self.max_momentum + 1
                self.current_speed -= 1
                results.append('{} loses speed due to {}'.format(self.owner.name, reason))
        return results


def can_move_direction(entity, neighbor, game_map):
    """
    Returns True if entity movement is not blocked
    :param entity: Entity trying to move
    :param neighbor: Tuple coordinates of next hex in direction of travel
    :param game_map: current game map
    :return: Boolean - True if Entity is able to move
    """
    new_x, new_y = neighbor
    if not game_map.in_bounds(x=new_x, y=new_y, margin=1):
        return False
    elif game_map.in_bounds(x=new_x, y=new_y) \
            and game_map.terrain[new_x][new_y].elevation > Elevation.SHALLOWS \
            and not entity.wings:
        return False
    return True
