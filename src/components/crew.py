from random import choice, randint
from src.map_objects.map_utils import get_hex_neighbors
from src.death_functions import kill_monster


class Crew:
    def __init__(self, size: int, crew: int):
        self.max_crew = size * 10 + 5
        if crew > self.max_crew:
            crew = self.max_crew
        self.crew = self.starting_crew(crew)
        
    def starting_crew(self, crew):
        crew_list = []
        for i in range(0, crew):
            member = Crewman()
            crew_list.append(member)
            print('Crewman {} the {} added'.format(member.name, member.profession))
        return crew_list
    
    def take_damage(self, amount: int, message_log):
        for i in range(amount):
            if len(self.crew) > 0:
                dead_man = randint(0, len(self.crew) - 1)
                message_log.add_message('Crewman {} the {} has died!'.format(self.crew[dead_man].name,
                                                                             self.crew[dead_man].profession),
                                        (200, 150, 40))
                del self.crew[dead_man]
                if len(self.crew) < 1:
                    message_log.add_message('{} has died!'.format(self.owner.name), (200, 150, 40))
                    return True
        return False

    def add_crew(self, crewman):
        if len(self.crew) + 1 > self.max_crew:
            return {'message': 'No room on ship for more crew'}
        else:
            self.crew.append(crewman)
            return {'message': 'Crewman {} the {} added'.format(crewman.name, crewman.profession)}

    def arrow_attack(self, terrain, entities, message_log, icons):
        total_damage = 1 + len(self.crew) // 10
        target_hexes = get_hex_neighbors(self.owner.x, self.owner.y)
        target_hexes.append((self.owner.x, self.owner.y))
        targeted_entities = [entity for entity in entities if
                             (entity.x, entity.y) in target_hexes and entity.fighter and not entity.name == 'player']
        for entity in targeted_entities:
            amount = total_damage // len(targeted_entities)
            # message_log.add_message('{} {} takes {} damage!'.format(entity.name, entity.fighter.name, amount),
            #                         (200, 150, 40))
            dead_result = entity.fighter.take_damage(amount, message_log)
            if dead_result:  # entity is dead
                kill_monster(terrain[entity.x][entity.y].elevation.value, entity, icons)
    
    def verify_arrow_target(self, entities):
        target_hexes = get_hex_neighbors(self.owner.x, self.owner.y)
        target_hexes.append((self.owner.x, self.owner.y))
        for entity in entities:
            if entity.fighter and (entity.x, entity.y) in target_hexes and not entity.name == 'player':
                return True
        return False


class Crewman:
    def __init__(self):
        self.name = self.generate_name
        self.profession = self.generate_profession
    
    @property
    def generate_name(self):
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
