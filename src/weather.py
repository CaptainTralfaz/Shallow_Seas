from enum import Enum
from random import randint


class Weather:
    def __init__(self):
        self.conditions = Conditions.CALM
        self.turn_count = 0
        self.max_turn_count = 50
        
    def calms(self, message_log, color):
        if self.conditions == Conditions.STORMY:
            self.conditions = Conditions.RAINY
            self.turn_count = 0
            message_log.add_message("The storm clears a bit", color)
        elif self.conditions == Conditions.RAINY:
            self.conditions = Conditions.CLOUDY
            self.turn_count = 0
            message_log.add_message("The rain stops", color)
        elif self.conditions == Conditions.CLOUDY:
            self.conditions = Conditions.HAZY
            self.turn_count = 0
            message_log.add_message("The clouds disperse", color)
        elif self.conditions == Conditions.HAZY:
            self.conditions = Conditions.CALM
            self.turn_count = 0
            message_log.add_message("The sky clears", color)
        else:
            self.turn_count += 1

    def worsens(self, message_log, color):
        if self.conditions == Conditions.CALM:
            self.conditions = Conditions.HAZY
            self.turn_count = 0
            message_log.add_message("A haze is in the air", color)
        elif self.conditions == Conditions.HAZY:
            self.conditions = Conditions.CLOUDY
            self.turn_count = 0
            message_log.add_message("Clouds gather in the sky", color)
        elif self.conditions == Conditions.CLOUDY:
            self.conditions = Conditions.RAINY
            self.turn_count = 0
            message_log.add_message("Rain begins to fall", color)
        elif self.conditions == Conditions.RAINY:
            self.conditions = Conditions.STORMY
            self.turn_count = 0
            message_log.add_message("STORM! Batten down the hatches!", color)
        else:
            self.turn_count += 1
        
    @property
    def get_weather_info(self):
        if self.conditions == Conditions.CALM:
            return weather_effects[Conditions.CALM]
        elif self.conditions == Conditions.HAZY:
            return weather_effects[Conditions.HAZY]
        elif self.conditions == Conditions.CLOUDY:
            return weather_effects[Conditions.CLOUDY]
        elif self.conditions == Conditions.RAINY:
            return weather_effects[Conditions.RAINY]
        elif self.conditions == Conditions.STORMY:
            return weather_effects[Conditions.STORMY]

        
def change_weather(weather, message_log, color):
    delay = 10  # leave weather for at least this many turns
    change_chance = randint(0, weather.max_turn_count)
    if change_chance + delay < weather.turn_count:
        # change weather 0: calmer
        #                1: stays
        #                2: rougher
        change = randint(0, 8)
        if change in [0, 1, 2]:
            weather.calms(message_log, color)
        elif change in [3, 4, 5]:
            weather.turn_count += 1
        else:
            weather.worsens(message_log, color)
    else:
        weather.turn_count += 1


class Conditions(Enum):
    CALM = 0
    HAZY = 1
    CLOUDY = 2
    RAINY = 3
    STORMY = 4


weather_effects = {Conditions.CALM: {'name': 'Calm', 'view': 1, 'fog': 0},
                   Conditions.HAZY: {'name': 'hazy', 'view': 0, 'fog': 2},
                   Conditions.CLOUDY: {'name': 'cloudy', 'view': 0, 'fog': 5},
                   Conditions.RAINY: {'name': 'rainy', 'view': -1, 'fog': 10},
                   Conditions.STORMY: {'name': 'stormy', 'view': -2, 'fog': 15}
                   }


