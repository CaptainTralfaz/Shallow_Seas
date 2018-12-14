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
