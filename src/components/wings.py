from src.components.masts import with_wind, against_wind, cross_wind


class Wings:
    def __init__(self, name: str, wings: int, size: int):
        """
        Component detailing a ship's masts and sails
        TODO: methods for new mast / sail built in port
        :param name: string name of component (was going to use this for wings too, but made seperate compnent)
        :param wings: int number of masts ship starts with
        :param size: int Size of the Entity (used to determine number of masts possible)
        """
        self.name = name
        self.size = size
        self.max_wing_power = wings
        self.current_wing_power = 0
        self.catching_wind = False
        self.wing_hp = size + 3
    
    def adjust_wings(self, amount: int):
        """
        Raise or Lower wing power
        :param amount: int amount of sails to raise / lower
        :return: list of str for message log
        """
        self.current_wing_power += amount
        if self.current_wing_power < 0:
            self.current_wing_power = 0
        elif self.current_wing_power > self.max_wing_power:
            self.current_wing_power = self.max_wing_power
    
    def take_wing_damage(self, amount):
        """
        Damages wing, removes it if necessary
        :param amount: int amount of damage done to wing
        :return: list of strings for message log
        """
        self.wing_hp -= amount
        if self.wing_hp < 0:
            self.max_wing_power -= 1
            if self.current_wing_power > self.max_wing_power:
                self.current_wing_power = self.max_wing_power
            if self.max_wing_power > 0:
                self.wing_hp = self.size * 2 + 2
    
    def repair_wings(self, amount):
        """
        Repair wings
        :param amount: int amount to add to wing HPs
        :return: list of str for message log
        """
        self.wing_hp += amount
        if self.wing_hp > self.size * 2 + 2:
            self.wing_hp = self.size * 2 + 2
    
    def momentum_due_to_wind(self, wind_direction: int,  message_log, color):
        """
        Adjust momentum due to wind: +2 per wing power if traveling with wind,
                                     +1 per wing power if direction is off by 1 facing
                                     -1 per wing power if traveling against wind
        :param wind_direction: int direction of wind
        :param message_log: current message log
        :param color: tuple for message color
        :return: int amount to change momentum by
        """
        results = []
        if with_wind(self.owner.mobile.direction, wind_direction):  # with wind: +2 momentum
            message_log.add_message(message='{} catches wind'.format(self.owner.name), color=color)
            results = self.owner.mobile.increase_momentum(amount=2 * self.current_wing_power, reason='wind')
            self.catching_wind = True  # no drag this turn
            return results
        elif cross_wind(self.owner.mobile.direction, wind_direction):  # cross wind: +1 momentum
            message_log.add_message(message='{} catches wind'.format(self.owner.name), color=color)
            results = self.owner.mobile.increase_momentum(amount=self.current_wing_power, reason='wind')
            self.catching_wind = True  # no drag this turn
            return results
        elif against_wind(self.owner.mobile.direction, wind_direction):  # against wind: -1 momentum
            message_log.add_message(message='{} catches reverse wind'.format(self.owner.name), color=color)
            results = self.owner.mobile.decrease_momentum(amount=-self.current_wing_power, reason='reverse wind')
            self.catching_wind = False  # drag this turn
            return results
        else:
            self.catching_wind = False  # drag this turn
            return results
