from src.map_objects.map_utils import hex_directions


class Masts:
    def __init__(self, masts: int, size: int):
        self.size = size
        self.masts = masts
        self.max_sails = masts
        self.current_sails = 0
        self.catching_wind = False
        self.mast_hp = size + 3
        self.sail_hp = size * 2 + 2
    
    def adjust_sails(self, amount: int):
        self.current_sails += amount
        if self.current_sails < 0:
            self.current_sails = 0
        elif self.current_sails > self.max_sails:
            self.current_sails = self.max_sails
    
    # update sprite sheet, but... need constants... will need to refactor
    
    def take_sail_damage(self, amount):
        self.sail_hp -= amount
        if self.sail_hp < 0:
            self.max_sails -= 1
            if self.current_sails > self.max_sails:
                self.current_sails = self.max_sails
            if self.max_sails > 0:
                self.sail_hp = self.size * 2 + 2
    
    def take_mast_damage(self, amount):
        self.mast_hp -= amount
        if self.mast_hp < 0:
            self.masts -= 1
            if self.max_sails > self.masts:
                self.max_sails = self.masts
                if self.current_sails > self.max_sails:
                    self.current_sails = self.max_sails
            if self.masts > 0:
                self.mast_hp += self.size + 3
    
    def repair_sails(self, amount):
        self.sail_hp += amount
        if self.sail_hp > self.size * 2 + 2:
            self.sail_hp = self.size * 2 + 2
    
    def repair_masts(self, amount):
        self.mast_hp += amount
        if self.mast_hp > self.size + 3:
            self.mast_hp = self.size + 3
    
    # TODO: move to Masts class
    def momentum_due_to_wind(self, wind_direction: int):
        if with_wind(self.owner.mobile.direction, wind_direction):  # with wind: +2 momentum
            self.owner.mobile.change_momentum(amount=2 * self.current_sails)
            self.catching_wind = True
        elif cross_wind(self.owner.mobile.direction, wind_direction):  # cross wind: +1 momentum
            self.owner.mobile.change_momentum(amount=self.current_sails)
            self.catching_wind = True
        elif against_wind(self.owner.mobile.direction, wind_direction):  # against wind: -1 momentum
            self.owner.mobile.change_momentum(amount=-self.current_sails)
            self.catching_wind = False
        else:
            self.catching_wind = False


def with_wind(ship_direction: int, wind_direction: int):
    # print("ship Direction: {}, wind direction: {}".format(ship_direction, wind_direction))
    if ship_direction == wind_direction:
        return True
    else:
        return False


def cross_wind(ship_direction: int, wind_direction: int):
    rotate_left = wind_direction + 1
    if rotate_left >= len(hex_directions):
        rotate_left -= len(hex_directions)
    rotate_right = wind_direction - 1
    if rotate_right < 0:
        rotate_right += len(hex_directions)
    if ship_direction == rotate_right or ship_direction == rotate_left:
        return True
    else:
        return False


def against_wind(ship_direction: int, wind_direction: int):
    rotate_left = wind_direction + 3
    if rotate_left > len(hex_directions):
        rotate_left -= len(hex_directions)
    rotate_right = wind_direction - 3
    if rotate_right < 0:
        rotate_right += len(hex_directions)
    if ship_direction == rotate_left or ship_direction == rotate_right:
        return True
    else:
        return False
