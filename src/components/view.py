from src.map_objects.map_utils import get_fov


class View:
    def __init__(self, view):
        self.view = view
        self.fov = {}
    
    def set_fov(self, game_map, game_time, game_weather):
        """
        :param game_map: the current map being played on
        :return: Nothing - modify current map
        """
        # get list of visible tiles
        port = None
        visible_tiles = get_fov(self, game_map, game_time, game_weather)
        if self.owner.name == 'player':
            for (x, y) in visible_tiles:
                if (0 <= x < game_map.width) and (0 <= y < game_map.height) and not game_map.terrain[x][y].seen:
                    game_map.terrain[x][y].seen = True
        else:  # not the player, remove port from fov
            # print(visible_tiles, len(visible_tiles))
            for x, y in visible_tiles:
                if game_map.terrain[x][y].decoration and game_map.terrain[x][y].decoration.name == 'Port':
                    port = (x, y)
        
        if port:
            visible_tiles.remove(port)
        # replace old visible list
        self.fov = visible_tiles
        # print(self.owner.name, self.fov)
