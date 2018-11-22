class Terrain:
    def __init__(self, x, y, elevation):
        self.elevation = elevation
        self.x = x
        self.y = y
        self.seen = False
        self.fog = False
        self.decoration = None
        
        if self.elevation == 0:
            self.name = 'Deeps'
            self.icon = 'deeps'
            self.color = 'light_blue'
        elif self.elevation == 1:
            self.name = 'Water'
            self.icon = 'water'
            self.color = 'blue'
        elif self.elevation == 2:
            self.name = 'Shallows'
            self.icon = 'shallows'
            self.color = 'aqua'
        elif self.elevation == 3:
            self.name = 'Dunes'
            self.icon = 'sand'
            self.color = 'cantaloupe'
        elif self.elevation == 4:
            self.name = 'Grassland'
            self.icon = 'grass'
            self.color = 'light_green'
        elif self.elevation == 5:
            self.name = 'Jungle'
            self.icon = 'forest'
            self.color = 'medium_green'
        elif self.elevation == 6:
            self.name = 'Mountain'
            self.icon = 'mountain'
            self.color = 'text'
        elif self.elevation >= 7:
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
            self.color = 'purple'
