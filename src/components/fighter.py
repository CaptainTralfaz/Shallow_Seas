class Fighter:
    def __init__(self, name: str, hps: int):
        self.name = name
        self.max_hps = hps
        self.hps = hps
    
    def take_damage(self, amount: int, message_log):
        self.hps -= amount
        message_log.add_message('{} {} is damaged for {}'.format(self.owner.name, self.name, amount), (200, 150, 40))
        if self.hps < 1:
            message_log.add_message('{} {} is destroyed!'.format(self.owner.name, self.name), (200, 150, 40))
            return True
        return False
        
    def heal_damage(self, amount: int):
        self.hps += amount
        if self.hps > self.max_hps:
            self.hps = self.max_hps
