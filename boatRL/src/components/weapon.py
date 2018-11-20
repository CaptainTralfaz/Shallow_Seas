class Weapon:
    def __init__(self, name, location, min_range, max_range, structure_points,  damage, effects):
        self.name = name
        self.location = location
        self.min_range = min_range
        self.max_range = max_range
        self.current_sp = structure_points
        self.max_sp = structure_points
        self.damage = damage
        self.effects = effects
        
    def take_damage(self, amount):
        messages = []
        self.current_sp -= amount
        if self.current_sp <= 0:
            # destroy the weapon
            messages.append({'message': 'A {} at the {} was destroyed!'.format(self.name, self.location)})
        else:
            messages.append({'message': 'A {} at the {} took {} damage!'.format(self.name, self.location, amount)})
        return messages

    def repair(self, amount):
        messages = []
        self.current_sp += amount
        if self.current_sp >= self.max_sp:
            self.current_sp = self.max_sp
            messages.append({'message': 'A {} at the {} was fully repaired!'.format(self.name, self.location)})
        else:
            messages.append({'message': 'A {} at the {} was partially repaired.'.format(self.name, self.location)})
        return messages
