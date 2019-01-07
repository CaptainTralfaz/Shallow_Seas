class Fighter:
    def __init__(self, name: str, hps: int):
        """
        Component detailing HPs
        :param name: str name of part with HPs (ex: 'hull', 'body', 'structure', etc.
        :param hps: int amount of maximum HPs
        """
        self.name = name
        self.max_hps = hps
        self.hps = hps
    
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
