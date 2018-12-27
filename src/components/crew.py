from src.map_objects.map_utils import get_hex_neighbors
from src.death_functions import kill_monster


class Crew:
    def __init__(self, size: int, crew: int):
        self.max_crew = size * 10 + 5
        if crew > self.max_crew:
            crew = self.max_crew
        self.crew = crew
        
    def take_crew_damage(self, amount: int):
        self.crew -= amount
        if self.crew < 1:
            return {"message": "All crew are dead. You Lose"}
        return {"message": "Ouch! {} of your crew have died".format(amount)}

    def add_crew(self, amount: int):
        if self.crew + amount > self.max_crew:
            return {'message': 'No room on ship for more crew'}
        else:
            self.crew += amount
            return {'message': 'Crew added'}

    def arrow_attack(self, terrain, entities, message_log, icons):
        total_damage = 1 + self.crew // 10
        target_hexes = get_hex_neighbors(self.owner.x, self.owner.y)
        target_hexes.append((self.owner.x, self.owner.y))
        targeted_entities = [entity for entity in entities if
                             (entity.x, entity.y) in target_hexes and entity.fighter and not entity.name == 'player']
        for entity in targeted_entities:
            amount = total_damage // len(targeted_entities)
            message_log.add_message('{} {} takes {} damage!'.format(entity.name, entity.fighter.name, amount),
                                    (200, 150, 40))
            message, dead_result = entity.fighter.take_damage(amount)
            if dead_result:  # entity is dead
                kill_monster(terrain[entity.x][entity.y].elevation.value, entity, icons)
            message_log.add_message(message)
    
    def verify_arrow_target(self, entities):
        target_hexes = get_hex_neighbors(self.owner.x, self.owner.y)
        target_hexes.append((self.owner.x, self.owner.y))
        for entity in entities:
            if entity.fighter and (entity.x, entity.y) in target_hexes and not entity.name == 'player':
                return True
        return False
