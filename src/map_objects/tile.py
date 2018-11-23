from enum import Enum


class Terrain:
    def __init__(self, elevation):
        self.elevation = Elevation(elevation)
        self.seen = False
        self.fog = False
        self.decoration = None
        
        if self.elevation == Elevation.DEEPS:
            self.name = 'Deeps'
            self.icon = 'deeps'
            self.color = 'light_blue'
        elif elevation == Elevation.WATER:
            self.name = 'Water'
            self.icon = 'water'
            self.color = 'blue'
        elif self.elevation == Elevation.SHALLOWS:
            self.name = 'Shallows'
            self.icon = 'shallows'
            self.color = 'aqua'
        elif self.elevation == Elevation.DUNES:
            self.name = 'Dunes'
            self.icon = 'sand'
            self.color = 'cantaloupe'
        elif self.elevation == Elevation.GRASSLAND:
            self.name = 'Grassland'
            self.icon = 'grass'
            self.color = 'light_green'
        elif self.elevation == Elevation.JUNGLE:
            self.name = 'Jungle'
            self.icon = 'jungle'
            self.color = 'medium_green'
        elif self.elevation == Elevation.MOUNTAIN:
            self.name = 'Mountain'
            self.icon = 'mountain'
            self.color = 'text'
        elif self.elevation == Elevation.VOLCANO:
            self.name = 'Volcano'
            self.icon = 'volcano'
            self.color = 'light_red'


class Decoration:
    def __init__(self, name):
        self.name = name
        self.icon = None
        self.color = None
        
        if self.name == 'Rocks':
            self.icon = 'rocks'
            self.color = 'text'
        elif self.name == 'Coral':
            self.icon = 'coral'
            self.color = 'carnation'
        elif self.name == 'Sandbar':
            self.icon = 'sandbar'
            self.color = 'cantaloupe'
        elif self.name == 'Seaweed':
            self.icon = 'seaweed'
            self.color = 'medium_green'
        elif self.name == 'Town':
            self.icon = 'town'
            self.color = 'black'


class Elevation(Enum):
    DEEPS = 0
    WATER = 1
    SHALLOWS = 2
    DUNES = 3
    GRASSLAND = 4
    JUNGLE = 5
    MOUNTAIN = 6
    VOLCANO = 7
