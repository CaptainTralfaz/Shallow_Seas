class Tile:
    """
    A tile on a map. It may or may not be blocked, and may or may not block sight.
    """
    
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        
        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        
        self.block_sight = block_sight


class Terrain:
    def __init__(self, x, y, height, icons, colors):
        self.height = height
        self.x = x
        self.y = y
        
        if self.height == 0:
            self.icon = icons['deeps']
            self.color = colors['dark_blue']
        elif self.height == 1:
            self.icon = icons['water']
            self.color = colors['blue']
        elif self.height == 2:
            self.icon = icons['shallows']
            self.color = colors['aqua']
        elif self.height == 3:
            self.icon = icons['sand']
            self.color = colors['cantaloupe']
        elif self.height == 4:
            self.icon = icons['grass']
            self.color = colors['green']
        elif self.height == 5:
            self.icon = icons['forest']
            self.color = colors['dark_green']
        elif self.height == 6:
            self.icon = icons['mountain']
            self.color = colors['brown']
        elif self.height > 7:
            self.icon = icons['volcano']
            self.color = colors['red']
