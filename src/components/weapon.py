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
    "Size.HUGE": {"Bow": 2,
                  "Port": 4,
                  "Stern": 2,
                  "Starboard": 4}
}


class WeaponList:
    def __init__(self):
        """
        Component holding list of Weapon objects
        """
        self.weapon_list = []
    
    def add_all(self, size):  # TODO remove this later - just here to initialize a ship's weapons
        """
        Quick and dirty way to initial all ship weapons to ballistas
        :param size: Size of the entity
        :return: None
        """
        for slot in max_weapons[size]:
            for w in range(max_weapons[size][slot]):
                self.weapon_list.append(Weapon("Ballista", slot, 1, 4, 5, 3, cool_down=4))
    
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
                                       icons=icons,
                                       elevation = terrain[entity.x][entity.y].elevation.value)
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
    def __init__(self, name, location, min_range, max_range, structure_points, damage, cool_down=None, effects=None):
        """
        
        :param name: str name of Weapon
        :param location: location of Weapon on Entity
        :param min_range: int minimum tile range for Weapon
        :param max_range: int maximum tile range for Weapon
        :param structure_points: HP's of Weapon
        :param damage: int damage dealt by Weapon
        :param cool_down: int cooldown in turns of Weapon
        :param effects: any special effects caused by Weapon
        """
        self.name = name
        self.location = location
        self.min_range = min_range
        self.max_range = max_range
        self.hps = structure_points
        self.max_hps = structure_points
        self.damage = damage
        self.cool_down = cool_down
        self.current_cd = 0
        self.effects = effects
    
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
