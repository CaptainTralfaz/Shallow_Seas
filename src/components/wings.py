from components.masts import with_wind, against_wind, cross_wind


class Wings:
    def __init__(self, name: str, wings: int, size: int=None, max_wing_power: int=None, current_wing_power: int=0,
                 catching_wind: bool=False, wing_hp_max: int=None, wing_hp: int=None):
        """
        Component detailing Entity Wing component
        TODO: methods for new mast / sail built in port
        :param name: string name of component
        :param wings: int number of wings Entity starts with
        :param size: int Size of the Entity (used to determine HPs of wings)
        :param max_wing_power: int maximum amount of power put into wings
        :param current_wing_power: int current amount of power put into wings
        :param catching_wind: boolean if wings are catching wind
        :param wing_hp_max: int maximum HPs of wing
        :param wing_hp: int current HPs of wing
        """
        self.name = name
        self.wings = wings
        self.max_wing_power = max_wing_power if max_wing_power is not None else wings          # max_sails
        self.current_wing_power = current_wing_power                                           # current_sails
        self.catching_wind = catching_wind
        self.wing_hp_max = wing_hp_max if wing_hp_max is not None else size + 3                # sail_hp_max
        self.wing_hp = wing_hp if wing_hp is not None else wing_hp_max                         # sail_hp

    def to_json(self):
        """
        Serialize Wings component to json
        :return: json serialized Wings component
        """
        return {
            'name': self.name,
            'wings': self.wings,
            'max_wing_power': self.max_wing_power,
            'current_wing_power': self.current_wing_power,
            'catching_wind': self.catching_wind,
            'wing_hp_max': self.wing_hp_max,
            'wing_hp': self.wing_hp
        }

    @staticmethod
    def from_json(json_data):
        """
        Convert json serialized Wings data to Masts component
        :param json_data: serialized Wings data
        :return: Wings component
        """
        name = json_data.get('name')
        wings = json_data.get('wings')
        max_wing_power = json_data.get('max_wing_power')
        current_wing_power = json_data.get('current_wing_power')
        catching_wind = json_data.get('catching_wind')
        wing_hp_max = json_data.get('wing_hp_max')
        wing_hp = json_data.get('wing_hp')
    
        return Wings(name=name, wings=wings, max_wing_power=max_wing_power, current_wing_power=current_wing_power,
                     catching_wind=catching_wind, wing_hp_max=wing_hp_max, wing_hp=wing_hp)

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
                self.wing_hp = self.owner.size * 2 + 2
    
    def repair_wings(self, amount):
        """
        Repair wings
        :param amount: int amount to add to wing HPs
        :return: list of str for message log
        """
        self.wing_hp += amount
        if self.wing_hp > self.owner.size * 2 + 2:
            self.wing_hp = self.owner.size * 2 + 2
    
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
