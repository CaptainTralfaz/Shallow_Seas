from death_functions import kill_monster
from map_objects.map_utils import get_target_hexes_at_location

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
    "Size.HUGE": {"Bow": 1,
                  "Port": 4,
                  "Stern": 2,
                  "Starboard": 4}
}


class WeaponList:
    def __init__(self, weapon_list: list=[]):
        """
        Component holding list of Weapon objects
        """
        self.weapon_list = weapon_list
    
    def to_json(self):
        return [weapon.to_json() for weapon in self.weapon_list]
    
    @staticmethod
    def from_json(json_data):
        return WeaponList([Weapon.from_json(weapon) for weapon in json_data])
    
    def add_all(self, size):  # TODO remove this later - just here to initialize a ship's weapons
        """
        Quick and dirty way to initial all ship weapons to ballista
        :param size: Size of the entity
        :return: None
        """
        for slot in max_weapons[size]:
            for w in range(max_weapons[size][slot]):
                self.weapon_list.append(Weapon(name="Livewood Ballista", location=slot, min_range=1, max_range=4,
                                               structure_points=5, damage=3, cool_down=4,
                                               repair_with=["Wood", "Leather"]))
    
    def add_weapon(self, weapon, location, size):
        """
        Add a specific Weapon to an entity
        :param weapon: Weapon to be added
        :param location: Location to add Weapon: this can be Bow, Port, Stern, or Starboard
        :param size: Size of the entity - determines max weapon placement per facing
        :return: Message for message_log
        """
        if self.get_weapons_count_at_location(location) < max_weapons[size][location]:
            # add weapon
            self.weapon_list.append(weapon)
            return {'message': '{} added to {}'.format(weapon.name, weapon.location)}
        else:
            return {'message': 'No empty weapon slots for {} on {}'.format(weapon.name, weapon.location)}
    
    def get_weapons_count_at_location(self, location):
        """
        Counts the number of Weapons at a specific location
        :param location: location for Weapons on entity
        :return: int number of Weapons at that location
        """
        return len(self.get_weapons_at_location(location))
    
    def get_weapons_at_location(self, location):
        """
        Creates a list of Weapons at a specific location on an entity
        :param location: location for Weapons on entity
        :return: list of Weapons
        """
        return [weapon for weapon in self.weapon_list if weapon.location == location and weapon.current_cd == 0]
    
    def remove_weapon(self, weapon):
        """
        Removes a specific weapon from a list of weapons
        TODO: this may need work - not actually used yet
        :param weapon: Weapon to remove
        :return: Message for message log
        """
        self.weapon_list.remove(weapon)
        return {'message': 'Removed {} on {}'.format(weapon.name, weapon.location)}
    
    def attack(self, terrain, entities, location, message_log, icons, colors):
        """
        Attack with each weapon on an entity's particular location
        :param terrain: terrain grid of GameMap
        :param entities: list of Entities
        :param location: location for Weapons on entity
        :param message_log: game message log
        :param icons: dict of icons to pass to death function
        :param colors: colors for message log
        :return: None
        """
        weapons = self.get_weapons_at_location(location=location)
        target_hexes = []
        total_damage = 0
        for weapon in weapons:
            target_hexes.extend(get_target_hexes_at_location(player=self.owner,
                                                             location=location,
                                                             max_range=weapon.max_range))
            total_damage += weapon.damage
            weapon.current_cd = weapon.cool_down
        targeted_entities = [entity for entity in entities if (entity.x, entity.y) in target_hexes
                             and (entity.x, entity.y) in self.owner.view.fov and entity.fighter]
        for entity in targeted_entities:
            amount = total_damage // len(targeted_entities)
            dead_result, details = entity.fighter.take_damage(amount=amount)
            message_log.unpack(details=details, color=colors['amber'])
            if dead_result:  # entity is dead
                details = kill_monster(entity=entity,
                                       elevation=terrain[entity.x][entity.y].elevation.value)
                message_log.unpack(details=details, color=colors['amber'])
    
    def verify_target_at_location(self, attack, entities):
        """
        Returns true if a target exists for a particular attack from a facing
        :param attack: location of the attack
        :param entities: Entities on the GameMap
        :return: Boolean - True if Entity is in target hexes
        """
        weapon_list = self.get_weapons_at_location(location=attack)
        if len(weapon_list) > 0:  # make sure there is a weapon on that side
            attack_range = weapon_list[0].max_range
            target_hexes = get_target_hexes_at_location(player=self.owner, location=attack, max_range=attack_range)
            valid_target = False
            for entity in entities:
                if entity.fighter and (entity.x, entity.y) in target_hexes \
                        and (entity.x, entity.y) in self.owner.view.fov:
                    return True
            if not valid_target:  # no targets in range
                return False
        else:
            return False  # no weapons at that location
        return False


class Weapon:
    def __init__(self, name: str, location: str, min_range: int, max_range: int, structure_points: int, damage: int,
                 hps=None, cool_down=None, current_cd=0, can_hit_locations=None, effects=None, repair_with=None):
        """
        Object detailing Weapon components
        :param name: str name of Weapon
        :param location: str location of Weapon on Entity
        :param min_range: int minimum tile range for Weapon
        :param max_range: int maximum tile range for Weapon
        :param structure_points: int HP's of Weapon
        :param damage: int damage dealt by Weapon
        :param cool_down: int cooldown in turns of Weapon
        :param effects: str any special effects caused by Weapon
        """
        self.name = name
        self.location = location
        self.min_range = min_range
        self.max_range = max_range
        self.hps = hps if hps else structure_points
        self.max_hps = structure_points
        self.damage = damage
        self.cool_down = cool_down
        self.current_cd = current_cd
        if can_hit_locations is not None:
            self.can_hit = can_hit_locations
        else:
            self.can_hit = ['body', 'hull', 'mast', 'sail', 'wings', 'crew', 'weapons', 'cargo']
        self.effects = effects
        self.repair_with = repair_with
    
    def to_json(self):
        """
        Serialize Weapon Object to json
        :return: json Weapon representation
        """
        return {
            'name': self.name,
            'location': self.location,
            'min_range': self.min_range,
            'max_range': self.max_range,
            'hps': self.hps,
            'max_hps': self.max_hps,
            'damage': self.damage,
            'cool_down': self.cool_down,
            'current_cd': self.current_cd,
            'can_hit': self.can_hit,
            'effects': self.effects,
            'repair_with': self.repair_with
        }
    
    @staticmethod
    def from_json(json_data):
        """
        Convert json representation of Weapon to Weapon Object
        :param json_data: json representation of Weapon Object
        :return: Weapon Object
        """
        name = json_data.get('name')
        location = json_data.get('location')
        min_range = json_data.get('min_range')
        max_range = json_data.get('max_range')
        hps = json_data.get('hps')
        max_hps = json_data.get('max_hps')
        damage = json_data.get('damage')
        cool_down = json_data.get('cool_down')
        current_cd = json_data.get('current_cd')
        can_hit = json_data.get('can_hit')
        effects = json_data.get('effects')
        repair_with = json_data.get('repair_with')
        
        return Weapon(name=name, location=location, min_range=min_range, max_range=max_range, hps=hps,
                      structure_points=max_hps, damage=damage, cool_down=cool_down, current_cd=current_cd,
                      can_hit_locations=can_hit, effects=effects, repair_with=repair_with)
    
    def take_damage(self, amount):
        """
        Adjust Weapon HP value if it is damaged
        TODO: actually destroy damaged weapon if HP < 1
        :param amount: int amount of damage
        :return: Message for message log
        """
        results = []
        self.hps -= amount
        if self.hps <= 0:
            # destroy the weapon
            results.append({'message': 'A {}  was destroyed!'.format(self.name)})
        else:
            results.append({'message': 'A {} took {} damage!'.format(self.name, amount)})
        return results
    
    def repair(self, amount):
        """
        Repair a Weapon HP value
        :param amount: int amount of Weapon HP to add
        :return: Message for message log
        """
        results = []
        self.hps += amount
        if self.hps >= self.max_hps:
            self.hps = self.max_hps
            results.append({'message': 'A {} was fully repaired!'.format(self.name)})
        else:
            results.append({'message': 'A {} was repaired {} points.'.format(self.name, amount)})
        return results

