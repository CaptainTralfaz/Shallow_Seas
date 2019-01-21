class Fighter:
    def __init__(self, name: str, max_hps: int, hps: int = None):
        """
        Component detailing HPs
        :param name: str name of part with HPs (ex: 'hull', 'body', 'structure', etc.
        :param max_hps: int amount of maximum HPs
        :param hps: int amount of current HPs
        """
        self.name = name
        self.max_hps = max_hps
        self.hps = hps if hps is not None else max_hps
    
    def to_json(self):
        """
        Serialize Fighter Object to json
        :return: json Fighter representation
        """
        return {
            'name': self.name,
            'max_hps': self.max_hps,
            'hps': self.hps
        }
    
    @staticmethod
    def from_json(json_data):
        """
        Convert json Fighter object representation to Fighter Object
        :param json_data: json Fighter object representation
        :return: Fighter object
        """
        name = json_data.get('name')
        max_hps = json_data.get('max_hps')
        hps = json_data.get('hps')
        
        return Fighter(name=name, max_hps=max_hps, hps=hps)
    
    def take_damage(self, amount: int):
        """
        Entity takes HP damage
        :param amount: int amount of damage
        :return: boolean dead, list of str for message log
        """
        results = []
        self.hps -= amount
        results.append('{} {} is damaged for {}'.format(self.owner.name, self.name, amount))
        if self.hps < 1:
            results.append('{} {} is destroyed!'.format(self.owner.name, self.name))
            return True, results
        return False, results
    
    def heal_damage(self, amount: int):
        """
        Heal Entity HP
        :param amount: int amount of HP to heal
        :return: list of str for message log
        """
        message = ""
        results = []
        if self.hps + amount >= self.max_hps:
            amount = self.max_hps - self.hps
            message = "fully "
        self.hps += amount
        results.append("{} {}healed for {}".format(self.owner.name, message, amount))
        return results
