from enum import Enum
from random import randint


class Weather:
    def __init__(self, conditions=0, turn_count=0, max_turn_count=50):
        """
        Class detailing current weather and chance of change
        """
        self.conditions = Conditions(conditions)
        self.turn_count = turn_count
        self.max_turn_count = max_turn_count
    
    def to_json(self):
        """
        Serialize class to json
        :return: json version of class
        """
        return {
            'conditions': self.conditions.value,
            'turn_count': self.turn_count,
            'max_turn_count': self.max_turn_count
        }
    
    @staticmethod
    def from_json(json_weather):
        """
        Convert serialized json to Weather object
        :param json_weather: serialized json Weather
        :return: Weather object
        """
        conditions = json_weather.get('conditions')
        turn_count = json_weather.get('turn_count')
        max_turn_count = json_weather.get('max_turn_count')
        
        return Weather(conditions=conditions, turn_count=turn_count, max_turn_count=max_turn_count)
        
    def calms(self, message_log, color):
        """
        Weather calms - lower condition value
        :param message_log: MessageLog containing messages
        :param color: tuple color of the text
        :return: None
        """
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
        """
        Weather worsens - raise condition value
        :param message_log: MessageLog containing messages
        :param color: tuple color of the text
        :return: None
        """
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
        """
        Returns weather effects dictionary depending on the conditions
        :return: dict of weather effects
        """
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
    """
    Determine change in weather
    :param weather: current game weather
    :param message_log: MessageLog
    :param color: tuple color of text to add
    :return: None
    """
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
    """
    Enum of possible weather values
    """
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
