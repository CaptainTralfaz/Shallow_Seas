from random import choice, randint

from src.death_functions import kill_monster
from src.map_objects.map_utils import get_hex_neighbors


class Crew:
    def __init__(self, size: int, crew: int):
        """
        Component detailing crew
        :param size: Entity Size to determine maximum number of crew
        :param crew: current number of crew
        """
        self.max_crew = size * 10 + 5
        if crew > self.max_crew:
            crew = self.max_crew
        self.crew = self.starting_crew(crew)
    
    def starting_crew(self, crew):
        """
        Fills ship with the number of crew given
        :param crew: int max number of crew
        :return: list of generated crew
        """
        crew_list = []
        for i in range(0, crew):
            member = Crewman()
            crew_list.append(member)
            print('Crewman {} the {} added'.format(member.name, member.profession))
        return crew_list
    
    def take_damage(self, amount: int):
        """
        Kills crew members. Death if the last crewman dies
        :param amount: int number of crew to kill
        :return: True if the last crew member died, messages
        """
        details = []
        for i in range(amount):
            if len(self.crew) > 0:
                dead_man = randint(0, len(self.crew) - 1)
                details.append('Crewman {} the {} has died!'.format(self.crew[dead_man].name,
                                                                    self.crew[dead_man].profession))
                del self.crew[dead_man]
                if len(self.crew) < 1:
                    details.append('{} has died!'.format(self.owner.name))
                    return True, details
        return False, details
    
    def add_crew(self, crewman):
        """
        Adds a new crewman if there is room
        :param crewman: Crew member
        :return: Message
        """
        if len(self.crew) + 1 > self.max_crew:
            return {'message': 'No room on ship for more crew'}
        else:
            self.crew.append(crewman)
            return {'message': 'Crewman {} the {} added'.format(crewman.name, crewman.profession)}
    
    def arrow_attack(self, terrain, entities, message_log, icons, colors):
        """
        Attack neighboring Entities
        :param terrain: passed to fov
        :param entities: list of possible Entity targets
        :param message_log: the message log
        :param icons: passed to kill_monster
        :param colors: tuple dict for message colors
        :return: None
        """
        total_damage = 1 + len(self.crew) // 10
        target_hexes = get_hex_neighbors(self.owner.x, self.owner.y)
        target_hexes.append((self.owner.x, self.owner.y))
        targeted_entities = [entity for entity in entities if
                             (entity.x, entity.y) in target_hexes and entity.fighter and not entity.name == 'player']
        for entity in targeted_entities:
            amount = total_damage // len(targeted_entities)
            # message_log.add_message('{} {} takes {} damage!'.format(entity.name, entity.fighter.name, amount),
            #                         (200, 150, 40))
            dead_result, details = entity.fighter.take_damage(amount)
            message_log.unpack(details=details, color=colors['amber'])
            if dead_result:  # entity is dead
                details = kill_monster(entity, icons, terrain[entity.x][entity.y].elevation.value)
                message_log.unpack(details=details, color=colors['amber'])
    
    def verify_arrow_target(self, entities):
        """
        Makes sure there is an adjacent target for an arrow attack
        :param entities: list of possible entity targets
        :return: boolean True if attackable neighbor, else False
        """
        target_hexes = get_hex_neighbors(self.owner.x, self.owner.y)
        target_hexes.append((self.owner.x, self.owner.y))
        for entity in entities:
            if entity.fighter and (entity.x, entity.y) in target_hexes and not entity.name == 'player':
                return True
        return False


class Crewman:
    def __init__(self):
        """
        container for crew memeber
        """
        self.name = self.generate_name
        self.profession = self.generate_profession
    
    @property
    def generate_name(self):
        """
        Creates a name for a crewman
        TODO: move to Generator
        :return: str 'firstName + lastName'
        """
        possible_names = ['James',
                          'Porter',
                          'Jones',
                          'Filmore',
                          'Jones',
                          'Ham',
                          'Lawrence'
                          ]
        possible_surnames = ['Knox',
                             'Smythe',
                             'Carver',
                             'Tanner',
                             'Percival',
                             'White',
                             'Black'
                             ]
        return "{} {}".format(choice(possible_names), choice(possible_surnames))
    
    @property
    def generate_profession(self):
        """
        Assigns a profession to a crewman
        TODO: move to Generator
        :return: str profession name
        """
        possible_professions = ['Sailor',
                                'Cook',
                                'Archer',
                                'Seer',
                                'Butcher',
                                'Woodworker',
                                'Engineer',
                                'Vagrant'
                                ]
        return choice(possible_professions)
