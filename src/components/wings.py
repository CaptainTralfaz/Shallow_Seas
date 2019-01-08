from src.components.masts import with_wind, against_wind, cross_wind


class Wings:
    def __init__(self, name: str, wings: int, size: int):
        self.name = name
        self.size = size
        self.max_wing_power = wings
        self.current_wing_power = 0
        self.catching_wind = False
        self.wing_hp = size + 3
    
    def adjust_wings(self, amount: int):
        self.current_wing_power += amount
        if self.current_wing_power < 0:
            self.current_wing_power = 0
        elif self.current_wing_power > self.max_wing_power:
            self.current_wing_power = self.max_wing_power
    
    def take_sail_damage(self, amount):
        self.wing_hp -= amount
        if self.wing_hp < 0:
            self.max_wing_power -= 1
            if self.current_wing_power > self.max_wing_power:
                self.current_wing_power = self.max_wing_power
            if self.max_wing_power > 0:
                self.wing_hp = self.size * 2 + 2
    
    def repair_wings(self, amount):
        self.wing_hp += amount
        if self.wing_hp > self.size * 2 + 2:
            self.wing_hp = self.size * 2 + 2
    
    def momentum_due_to_wind(self, wind_direction: int):
        if with_wind(self.owner.mobile.direction, wind_direction):  # with wind: +2 momentum
            self.owner.mobile.increase_momentum(amount=2 * self.current_wing_power, reason='wind')
            self.catching_wind = True
            return 2 * self.current_wing_power
        elif cross_wind(self.owner.mobile.direction, wind_direction):  # cross wind: +1 momentum
            self.owner.mobile.increase_momentum(amount=self.current_wing_power, reason='wind')
            self.catching_wind = True
            return self.current_wing_power
        elif against_wind(self.owner.mobile.direction, wind_direction):  # against wind: -1 momentum
            self.owner.mobile.decrease_momentum(amount=-self.current_wing_power, reason='reverse wind')
            self.catching_wind = False
            return -self.current_wing_power
        else:
            self.catching_wind = False
            return
