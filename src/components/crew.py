from random import choice, randint

from death_functions import kill_monster
from map_objects.map_utils import get_hex_neighbors


class Crew:
    def __init__(self, size: int, crew_size: int = None, crew_list=None):
        """
        Component detailing crew
        :param size: Entity Size to determine maximum number of crew
        :paramn crew_size: int size of starting crew to add to crew list
        :param crew_list: list of current crewmen
        """
        self.max_crew = size * 10 + 5
        if crew_size > self.max_crew:
            crew_size = self.max_crew
        self.crew_list = crew_list if crew_list is not None else self.starting_crew(crew_size)
    
    def to_json(self):
        """
        Serialize Crew object to json
        :return: json representation of Crew object
        """
        return {
            'max_crew': self.max_crew,
            'crew_list': [Crewman.to_json(crewman) for crewman in self.crew_list]
        }
    
    @staticmethod
    def from_json(json_data):
        """
        Convert json representation Crew object to Crew Object
        :param json_data: json representation of Crew object
        :return: Crew Object
        """
        max_crew = json_data.get('max_crew')
        json_crew_list = json_data.get('crew_list')
        
        crew_list = [Crewman(name=crewman.get('name'), profession=crewman.get('profession'))
                     for crewman in json_crew_list]
        
        return Crew(size=max_crew, crew_list=crew_list)
    
    @staticmethod
    def starting_crew(crew_size):
        """
        Fills ship with the number of crew given
        :param crew_size: int current number of crew
        :return: list of generated crew
        """
        crew_list = []
        for i in range(0, crew_size):
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
            if len(self.crew_list) > 0:
                dead_man = randint(0, len(self.crew_list) - 1)
                details.append('Crewman {} the {} has died!'.format(self.crew_list[dead_man].name,
                                                                    self.crew_list[dead_man].profession))
                del self.crew_list[dead_man]
                if len(self.crew_list) < 1:
                    details.append('{} has died!'.format(self.owner.name))
                    return True, details
        return False, details
    
    def add_crew(self, crewman):
        """
        Adds a new crewman if there is room
        :param crewman: Crew member
        :return: Message
        """
        if len(self.crew_list) + 1 > self.max_crew:
            return {'message': 'No room on ship for more crew'}
        else:
            self.crew_list.append(crewman)
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
        total_damage = 1 + len(self.crew_list) // 10
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
                details = kill_monster(entity, terrain[entity.x][entity.y].elevation.value)
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
    def __init__(self, name: str = None, profession: str = None):
        """
        container for crew member
        :param name: str name of crewman
        :param profession: str profession of crewman
        """
        self.name = name if name else self.generate_name
        self.profession = profession if profession else self.generate_profession
    
    def to_json(self):
        return {
            'name': self.name,
            'profession': self.profession
        }
    
    @staticmethod
    def from_json(json_data):
        name = json_data.get('name')
        profession = json_data.get('profession')
        
        return Crewman(name, profession)
    
    @property
    def generate_name(self):
        """
        Creates a name for a crewman
        TODO: move to Factory
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
