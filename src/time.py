from enum import Enum


class Time:
    def __init__(self):
        self.hrs = 12
        self.min = 00
        self.day = 1
        self.month = 1
        self.year = 1111  # Year of Steve
    
    def roll_min(self):
        self.min += 2
        if self.min >= 60:
            self.min -= 60
            self.roll_hrs()
    
    def roll_hrs(self):
        self.hrs += 1
        if self.hrs > 23:
            self.hrs -= 24
            self.roll_day()
    
    def roll_day(self):
        self.day += 1
        if self.day > 30:
            self.day -= 30
            self.roll_month()
    
    def roll_month(self):
        self.month += 1
        if self.month > 12:
            self.month -= 12
            self.roll_year()
    
    def roll_year(self):
        self.year += 1
        if self.year > 1111:
            print("out of turns!")
    
    @property
    def get_time_of_day_info(self):
        if self.hrs in [1, 2]:
            return time_of_day_info[TimeOfDay.DEEPNIGHT]
        elif self.hrs in [3, 4]:
            return time_of_day_info[TimeOfDay.WEEHOURS]
        elif self.hrs in [5, 6]:
            return time_of_day_info[TimeOfDay.DAWN]
        elif self.hrs in [7, 8]:
            return time_of_day_info[TimeOfDay.MORNING]
        elif self.hrs in [9, 10]:
            return time_of_day_info[TimeOfDay.FORENOON]
        elif self.hrs in [11, 12]:
            return time_of_day_info[TimeOfDay.NOON]
        elif self.hrs in [13, 14]:
            return time_of_day_info[TimeOfDay.AFTERNOON]
        elif self.hrs in [15, 16]:
            return time_of_day_info[TimeOfDay.LATEDAY]
        elif self.hrs in [17, 18]:
            return time_of_day_info[TimeOfDay.EVENING]
        elif self.hrs in [19, 20]:
            return time_of_day_info[TimeOfDay.TWILIGHT]
        elif self.hrs in [21, 22]:
            return time_of_day_info[TimeOfDay.NIGHT]
        elif self.hrs in [23, 0]:
            return time_of_day_info[TimeOfDay.MIDNIGHT]
        else:
            return KeyError


class TimeOfDay(Enum):
    DAWN = 0
    MORNING = 1
    FORENOON = 2
    NOON = 3
    AFTERNOON = 4
    LATEDAY = 5
    EVENING = 6
    TWILIGHT = 7
    NIGHT = 8
    MIDNIGHT = 9
    DEEPNIGHT = 10
    WEEHOURS = 11
    
    
time_of_day_info = {TimeOfDay.DAWN: {'name': 'Dawn', 'begin': 5, 'view': 0, 'fog': 10, 'sky': 'carnation'},
                    TimeOfDay.MORNING: {'name': 'Morning', 'begin': 7, 'view': 0, 'fog': 5, 'sky': 'cyan'},
                    TimeOfDay.FORENOON: {'name': 'Forenoon', 'begin': 9, 'view': 0, 'fog': 0, 'sky': 'aqua'},
                    TimeOfDay.NOON: {'name': 'Noontime', 'begin': 11, 'view': 0, 'fog': 0, 'sky': 'aqua'},
                    TimeOfDay.AFTERNOON: {'name': 'Afternoon', 'begin': 13, 'view': 0, 'fog': 0, 'sky': 'aqua'},
                    TimeOfDay.LATEDAY: {'name': 'Late Day', 'begin': 15, 'view': 0, 'fog': 0, 'sky': 'cyan'},
                    TimeOfDay.EVENING: {'name': 'Evening', 'begin': 17, 'view': 0, 'fog': 0, 'sky': 'carnation'},
                    TimeOfDay.TWILIGHT: {'name': 'Twilight', 'begin': 19, 'view': -1, 'fog': 0, 'sky': 'violet'},
                    TimeOfDay.NIGHT: {'name': 'Night', 'begin': 21, 'view': -2, 'fog': 0, 'sky': 'black'},
                    TimeOfDay.MIDNIGHT: {'name': 'Midnight', 'begin': 23, 'view': -3, 'fog': 5, 'sky': 'black'},
                    TimeOfDay.DEEPNIGHT: {'name': 'Deep Night', 'begin': 1, 'view': -2, 'fog': 10, 'sky': 'black'},
                    TimeOfDay.WEEHOURS: {'name': 'Wee Hours', 'begin': 3, 'view': -1, 'fog': 15, 'sky': 'violet'}
                    }


# Dawn	5:30 - 7:25 A		10%
# Morning	7:30 - 9:25 A		5%
# Late Morning	9:30 - 11:25 A
# Noontime	11:30 - 1:25 A/P
# Afternoon	1:30 - 3:25 P
# Late Day	3:30 - 5:25 P
# Evening	5:30 - 7:25 P
# Twilight	7:30 - 9:25 P	-1
# Night	9:30 - 11:25 P	-2
# Midnight	11:30 - 1:25 P/A	-3	5%
# Deep Night	1:30 - 3:25 A	-2	10%
# Wee Hours	3:30 - 5:25 A	-1	15%

