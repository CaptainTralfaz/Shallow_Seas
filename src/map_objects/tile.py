from enum import Enum


class Decoration:
    def __init__(self, name: str, icon: str = None, color: str = None):
        """
        Decoration name, icon, and mini-map color
        :param name: determines the icon and mini-map color
        """
        self.name = name
        self.icon = icon
        self.color = color
        
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
        elif self.name == 'Port':
            self.icon = 'port'
            self.color = 'white'


class Terrain:
    def __init__(self, elevation: int, seen: bool=False, decoration: str=None, fog: bool=None):
        """
        Height of terrain determines the terrain Enum value, name, mini-map color, and icon
        This class will also track if the tile has been seen, contains fog, or contains a decoration
        :param elevation: int elevation height
        :param seen: boolean if tile has been in player's fov
        :param decoration: Decoration
        :param fog: int elevation height
        """
        self.elevation = Elevation(elevation)
        self.seen = seen
        self.decoration = decoration
        self.fog = fog
        
        if self.elevation == Elevation.DEEPS:
            self.name = 'Deep Sea'
            self.icon = 'deep_sea'
            self.color = 'light_blue'
        elif self.elevation == Elevation.WATER:
            self.name = 'Sea'
            self.icon = 'sea'
            self.color = 'blue'
        elif self.elevation == Elevation.SHALLOWS:
            self.name = 'Shallows'
            self.icon = 'shallows'
            self.color = 'aqua'
        elif self.elevation == Elevation.DUNES:
            self.name = 'Dunes'
            self.icon = 'dunes'
            self.color = 'cantaloupe'
        elif self.elevation == Elevation.GRASSLAND:
            self.name = 'Grassland'
            self.icon = 'grassland'
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
    
    def to_json(self):
        return {
            'elevation': self.elevation.value,
            'seen': self.seen,
            'decoration': self.decoration.name if self.decoration else None,
            'fog': self.fog
        }
    
    @staticmethod
    def from_json(json_tile):
        elevation = json_tile.get('elevation')
        seen = json_tile.get('seen')
        decoration = Decoration(json_tile.get('decoration')) if json_tile.get('decoration') else None
        fog = json_tile.get('fog')
        
        return Terrain(elevation=elevation, seen=seen, decoration=decoration, fog=fog)


class Elevation(Enum):
    """
    Enum to track elevation
    """
    DEEPS = 0
    WATER = 1
    SHALLOWS = 2
    DUNES = 3
    GRASSLAND = 4
    JUNGLE = 5
    MOUNTAIN = 6
    VOLCANO = 7
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    
    def __ne__(self, other):
        if self.__class__ is other.__class__:
            return self.value != other.value
        return NotImplemented
