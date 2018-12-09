from src.map_objects.map_utils import hex_directions
from src.map_objects.tile import Elevation


class Mobile:
    def __init__(self, direction, max_momentum, max_speed=2, speed=0):
        self.direction = direction
        self.max_momentum = max_momentum
        self.current_momentum = self.max_momentum
        self.max_speed = max_speed
        self.current_speed = speed
        self.rowing = False
        self.catching_wind = False
    
    def move(self, game_map):
        # Move the entity by their current_speed
        dx, dy = hex_directions[self.direction]
        for speed in range(0, self.current_speed):
            new_x = self.owner.x + dx
            if dx == 0:
                new_y = self.owner.y + dy
            else:
                new_y = self.owner.y + dy + self.owner.x % 2
            # check for collisions!
            # TODO: Send to collision method, as determined by movement type (sail, flying, swim/row, etc)
            if game_map.in_bounds(new_x, new_y) \
                    and game_map.terrain[new_x][new_y].decoration \
                    and game_map.terrain[new_x][new_y].decoration.name == 'Port' \
                    and self.owner.name is "player":
                print('{} sailed into Port'.format(self.owner.name))
                self.owner.x = new_x
                self.owner.y = new_y
                self.current_speed = 0
                self.current_momentum = 0
                if hasattr(self.owner, "mast_sail"):
                    self.owner.mast_sail.current_sails = 0
                break
            elif game_map.in_bounds(new_x, new_y) and \
                    game_map.terrain[new_x][new_y].elevation > Elevation.SHALLOWS \
                    and not self.owner.wings:
                print("{} crashed into island!".format(self.owner.name))
                # take damage depending on speed
                self.current_speed = 0
                self.current_momentum = self.max_momentum
                break
            else:
                # Just move
                self.owner.x = new_x
                self.owner.y = new_y
    
    def rotate(self, rotate: int):
        # print("old direction: {}".format(self.direction))
        # print("rotating: {}".format(rotate))
        self.direction += rotate
        if self.direction > len(hex_directions) - 1:
            self.direction -= len(hex_directions)
        elif self.direction < 0:
            self.direction += len(hex_directions)
        # self.owner.icon = rot_center(image=self.owner.icon, angle=direction_angle[self.direction])
        # print("new direction: {}".format(self.direction))
    
    def change_momentum(self, amount: int):
        self.current_momentum += amount
        # print(amount)
        if self.current_momentum > self.max_momentum:
            self.current_speed += 1
            self.current_momentum -= self.max_momentum + 1
            if self.current_speed > self.max_speed:
                self.current_speed = self.max_speed
                self.current_momentum = self.max_momentum
        if self.current_momentum < 0:
            self.current_speed -= 1
            self.current_momentum += self.max_momentum + 1
            if self.current_speed < 0:
                self.current_speed = 0
                self.current_momentum = 0
                # recreate icon from sprite sheet


def can_move_direction(neighbor, game_map):
    new_x, new_y = neighbor
    if not game_map.in_bounds(x=new_x, y=new_y, margin=1):
        return False
    # TODO: account for flyers
    elif game_map.in_bounds(new_x, new_y) \
            and game_map.terrain[new_x][new_y].elevation > Elevation.SHALLOWS:
        return False
    return True
