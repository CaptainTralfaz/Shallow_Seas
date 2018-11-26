class Weapon:
    def __init__(self, name, min_range, max_range, structure_points, damage, cool_down=None, effects=None):
        self.name = name
        self.min_range = min_range
        self.max_range = max_range
        self.current_sp = structure_points
        self.max_sp = structure_points
        self.damage = damage
        self.cool_down = cool_down
        self.current_cd = 0
        self.effects = effects

    def take_damage(self, amount):
        messages = []
        self.current_sp -= amount
        if self.current_sp <= 0:
            # destroy the weapon
            messages.append({'message': 'A {}  was destroyed!'.format(self.name)})
        else:
            messages.append({'message': 'A {} took {} damage!'.format(self.name, amount)})
        return messages

    def repair(self, amount):
        messages = []
        self.current_sp += amount
        if self.current_sp >= self.max_sp:
            self.current_sp = self.max_sp
            messages.append({'message': 'A {} was fully repaired!'.format(self.name)})
        else:
            messages.append({'message': 'A {} was repaired {} points.'.format(self.name, amount)})
        return messages
