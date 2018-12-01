from src.map_objects.map_utils import get_target_hexes_at_location

max_weapons = {
    "Size.TINY": {"Bow": 0,
                  "Port": 0,
                  "Stern": 0,
                  "Starboard": 0},
    "Size.SMALL": {"Bow": 0,
                   "Port": 1,
                   "Stern": 0,
                   "Starboard": 1},
    "Size.MEDIUM": {"Bow": 0,
                    "Port": 2,
                    "Stern": 1,
                    "Starboard": 2},
    "Size.LARGE": {"Bow": 1,
                   "Port": 3,
                   "Stern": 1,
                   "Starboard": 3},
    "Size.HUGE": {"Bow": 2,
                  "Port": 4,
                  "Stern": 2,
                  "Starboard": 4}
    }


class WeaponList:
    def __init__(self):
        self.weapon_list = []
        
    def add_all(self, size):  # TODO remove this later - just here to initialize a ship's weapons
        for slot in max_weapons[size]:
            for w in range(max_weapons[size][slot]):
                self.weapon_list.append(Weapon("Ballista", slot, 1, 4, 5, 3, cool_down=2))

    def add_weapon(self, weapon, location, size):
        if self.get_weapons_count_at_location(location) < max_weapons[size][location]:
            # add weapon
            self.weapon_list.append(weapon)
            return {'message': '{} added to {}'.format(weapon.name, weapon.location)}
        else:
            return {'message': 'No empty weapon slots for {} on {}'.format(weapon.name, weapon.location)}
        
    def get_weapons_count_at_location(self, location):
        return len(self.get_weapons_at_location(location))

    def get_weapons_at_location(self, location):
        return [weapon for weapon in self.weapon_list if weapon.location == location]

    def remove_weapon(self, weapon):
        self.weapon_list.remove(weapon)
        return {'message': 'Removed {} on {}'.format(weapon.name, weapon.location)}
        
    def attack(self, entities, location, message_log):
        weapons = self.get_weapons_at_location(location)
        target_hexes = []
        total_damage = 0
        for weapon in weapons:
            target_hexes.extend(get_target_hexes_at_location(self.owner, location, weapon.max_range))
            total_damage += weapon.damage
        targeted_entities = [entity for entity in entities if (entity.x, entity.y) in target_hexes]
        for entity in targeted_entities:
            amount = total_damage // len(targeted_entities)
            entity.fighter.take_damage(amount)
            message_log.add_message('{} takes {} damage!'.format(entity.name, amount), (200, 150, 40))


class Weapon:
    def __init__(self, name, location, min_range, max_range, structure_points, damage, cool_down=None, effects=None):
        self.name = name
        self.location = location
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

