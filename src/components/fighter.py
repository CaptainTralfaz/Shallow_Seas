class Fighter:
    def __init__(self, name: str, hps: int):
        self.name = name
        self.max_hps = hps
        self.hps = hps
    
    def take_damage(self, amount: int):
        self.hps -= amount
        if self.hps < 1:
            return '{} {} has died!'.format(self.owner.name, self.name)
        return '{} {} is wounded'.format(self.owner.name, self.name)

    def heal_damage(self, amount: int):
        self.hps += amount
        if self.hps > self.max_hps:
            self.hps = self.max_hps
