from map_objects.map_utils import hex_directions


class Masts:
    def __init__(self, name, masts, size=None, max_sails=None, current_sails=0, catching_wind=False, mast_hp_max=None,
                 mast_hp=None, sail_hp_max=None, sail_hp=None, sail_repair_with=None, mast_repair_with=None):
        """
        Component detailing a ship's masts and sails
        TODO: methods for new mast / sail built in port
        :param name: string name of component (was going to use this for wings too, but made separate component)
        :param masts: int number of masts ship starts with
        :param size: int Size of the Entity (used to determine number of masts possible & mast/sail HPs)
        :param max_sails: int maximum number of sails
        :param current_sails: int current number of sails raised
        :param catching_wind: boolean using wind propulsion (to prevent drag)
        :param mast_hp_max: int maximum hp of each mast
        :param mast_hp: int current hp of mast
        :param sail_hp_max: int maximum hp of each sail
        :param sail_hp: int current hp of sail
        """
        self.name = name
        self.masts = masts
        self.max_sails = max_sails if max_sails is not None else masts
        self.current_sails = current_sails
        self.catching_wind = catching_wind
        self.mast_hp_max = mast_hp_max if mast_hp_max is not None else size + 3
        self.mast_hp = mast_hp if mast_hp is not None else self.mast_hp_max
        self.sail_hp_max = sail_hp_max if sail_hp_max is not None else size * 2 + 2
        self.sail_hp = sail_hp if sail_hp is not None else size * 2 + 2
        self.sail_repair_with = sail_repair_with
        self.mast_repair_with = mast_repair_with

    def to_json(self):
        """
        Serialize Masts component to json
        :return: json serialized Masts component
        """
        return {
            'name': self.name,
            'masts': self.masts,
            'max_sails': self.max_sails,
            'current_sails': self.current_sails,
            'catching_wind': self.catching_wind,
            'mast_hp_max': self.mast_hp_max,
            'mast_hp': self.mast_hp,
            'sail_hp_max': self.sail_hp_max,
            'sail_hp': self.sail_hp,
            'sail_repair_with': self.sail_repair_with,
            'mast_repair_with': self.mast_repair_with
        }
    
    @staticmethod
    def from_json(json_data):
        """
        Convert json serialized Masts data to Masts component
        :param json_data: serialized Masts data
        :return: Masts component
        """
        name = json_data.get('name')
        masts = json_data.get('masts')
        max_sails = json_data.get('max_sails')
        current_sails = json_data.get('current_sails')
        catching_wind = json_data.get('catching_wind')
        mast_hp_max = json_data.get('mast_hp_max')
        mast_hp = json_data.get('mast_hp')
        sail_hp_max = json_data.get('sail_hp_max')
        sail_hp = json_data.get('sail_hp')
        sail_repair_with = json_data.get('sail_repair_with')
        mast_repair_with = json_data.get('mast_repair_with')

        return Masts(name=name, masts=masts, max_sails=max_sails, current_sails=current_sails,
                     catching_wind=catching_wind, mast_hp_max=mast_hp_max, mast_hp=mast_hp, sail_hp_max=sail_hp_max,
                     sail_hp=sail_hp, sail_repair_with=sail_repair_with, mast_repair_with=mast_repair_with)
    
    def adjust_sails(self, amount: int):
        """
        Raise or Lower sails
        :param amount: int amount of sails to raise / lower
        :return: list of str for message log
        """
        self.current_sails += amount
        results = []
        if amount > 0:
            results.append('Sails raised to {}'.format(self.current_sails))
        elif amount < 0:
            results.append('Sails lowered to {}'.format(self.current_sails))
        if self.current_sails < 0:
            self.current_sails = 0
            results.append('Sails all furled')
        elif self.current_sails > self.max_sails:
            self.current_sails = self.max_sails
            results.append('Sails at maximum')
        return results
    
    def take_sail_damage(self, amount):
        """
        Damages a sail, removes it if needed
        :param amount: amount of damage done to sail
        :return: list of str for message log
        """
        results = []
        self.sail_hp -= amount
        if self.sail_hp < 1 and self.max_sails > 0:
            self.max_sails -= 1
            results.append('Lost a Sail!')
            if self.current_sails > self.max_sails:
                self.current_sails = self.max_sails
            if self.max_sails > 0:
                self.sail_hp = self.owner.size * 2 + 2
        elif self.max_sails < 1:
            self.current_sails = 0
            self.max_sails = 0
            self.sail_hp = 0
            results.append('No sails left to damage')
        else:
            results.append('Sail takes {} damage'.format(amount))
        return False, results
    
    def take_mast_damage(self, amount):
        """
        Damages mast, removes it if necessary
        :param amount: int amount of damage done to mast
        :return: list of strings for message log
        """
        results = []
        if self.mast_hp - amount < 0:
            self.sail_hp -= amount
            self.masts -= 1
            message = 'Lost a mast'
            if self.max_sails > self.masts:
                self.max_sails = self.masts
                message += ', and a sail went with it'
                if self.current_sails > self.max_sails:
                    self.current_sails = self.max_sails
            message += '!'
            results.append(message)
            if self.masts > 0 and self.max_sails > 0:
                self.mast_hp += self.owner.size + 3
        else:
            self.sail_hp -= amount
            results.append('A mast took {} damage'.format(amount))
        return results

    def repair_sails(self, amount):
        """
        Repair sails
        :param amount: int amount to add to sail HPs
        :return: list of str for message log
        """
        results = []
        message = ""
        if self.sail_hp + amount >= self.owner.size * 2 + 2:
            amount = self.owner.size * 2 + 2 - self.sail_hp
            message = "fully "
        self.sail_hp += amount
        results.append("Sail {}repaired for {}".format(message, amount))
        return results
    
    def repair_masts(self, amount):
        """
        Repair masts
        :param amount: int amount to add to mast HPs
        :return: list of str for message log
        """
        results = []
        message = ""
        if self.mast_hp + amount >= self.owner.size + 3:
            amount = self.owner.size + 3 - self.mast_hp
            message = "fully "
        self.mast_hp += amount
        results.append("Mast {}repaired for {}".format(message, amount))
        return results

    def momentum_due_to_wind(self, wind_direction: int, message_log, color):
        """
        Adjust momentum due to wind: +2 per sail if traveling with wind,
                                     +1 per sail if direction is off by 1 facing
                                     -1 per sail if traveling against wind
        :param wind_direction: int direction of wind
        :param message_log: current message log
        :param color: tuple for message color
        :return: int amount to change momentum by
        """
        results = []
        if with_wind(self.owner.mobile.direction, wind_direction):  # with wind: +2 momentum
            message_log.add_message(message='{} catches wind'.format(self.owner.name), color=color)
            results = self.owner.mobile.increase_momentum(amount=2 * self.current_sails, reason='wind')
            self.catching_wind = True  # no drag this turn
            return results
        elif cross_wind(self.owner.mobile.direction, wind_direction):  # cross wind: +1 momentum
            message_log.add_message(message='{} catches wind'.format(self.owner.name), color=color)
            results = self.owner.mobile.increase_momentum(amount=self.current_sails, reason='wind')
            self.catching_wind = True  # no drag this turn
            return results
        elif against_wind(self.owner.mobile.direction, wind_direction):  # against wind: -1 momentum
            message_log.add_message(message='{} catches reverse wind'.format(self.owner.name), color=color)
            results = self.owner.mobile.decrease_momentum(amount=-self.current_sails, reason='reverse wind')
            self.catching_wind = False  # drag this turn
            return results
        else:
            self.catching_wind = False  # drag this turn
            return results


def with_wind(entity_direction: int, wind_direction: int):
    """
    Returns true if Entity traveling same direction as wind
    :param entity_direction: Entity direction
    :param wind_direction: wind direction
    :return: Boolean
    """
    if entity_direction == wind_direction:
        return True
    else:
        return False


def cross_wind(entity_direction: int, wind_direction: int):
    """
    Returns true if Entity one facing away from wind direction
    :param entity_direction: Entity direction
    :param wind_direction: wind direction
    :return: Boolean
    """
    rotate_left = wind_direction + 1
    if rotate_left >= len(hex_directions):
        rotate_left -= len(hex_directions)
    rotate_right = wind_direction - 1
    if rotate_right < 0:
        rotate_right += len(hex_directions)
    if entity_direction == rotate_right or entity_direction == rotate_left:
        return True
    else:
        return False


def against_wind(entity_direction: int, wind_direction: int):
    """
    Returns true if Entity traveling opposite direction of wind
    :param entity_direction: Entity direction
    :param wind_direction: wind direction
    :return: Boolean
    """
    rotate_left = wind_direction + 3
    if rotate_left > len(hex_directions):
        rotate_left -= len(hex_directions)
    rotate_right = wind_direction - 3
    if rotate_right < 0:
        rotate_right += len(hex_directions)
    if entity_direction == rotate_left or entity_direction == rotate_right:
        return True
    else:
        return False
