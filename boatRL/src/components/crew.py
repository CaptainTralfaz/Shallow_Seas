class Crew:
    def __init__(self, size: int, crew: int):
        self.max_crew = size * 5 + 5
        self.crew = crew
    
    def take_crew_damage(self, amount: int):
        self.crew -= amount
        if self.crew < 1:
            return {"message": "dead"}
        return {"message": "ouch"}
