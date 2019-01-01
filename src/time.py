class Time:
    def __init__(self):
        self.hrs = 12
        self.min = 00
        self.day = 1
        self.month = 1
        self.year = 1111  # Year of Steve
    
    def roll_min(self):
        self.min += 5
        if self.min >= 60:
            self.min = 0
            self.roll_hrs()
    
    def roll_hrs(self):
        self.hrs += 1
        if self.hrs > 24:
            self.hrs = 1
            self.roll_day()
    
    def roll_day(self):
        self.day += 1
        if self.day > 30:
            self.day = 1
            self.roll_month()
    
    def roll_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.roll_year()
    
    def roll_year(self):
        self.year += 1
        if self.year > 1111:
            print("out of turns!")
