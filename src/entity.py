class Entity:
    """
    A generic object to represent ships, enemies, etc.
    """
    
    def __init__(self, name, x, y, icon, ai=None, block_view=None, elevation=None, mobile=None,
                 size=None, view=None, crew=None, mast_sail=None, weapons=None, wings=None,
                 cargo=None, sprite_sheet=None):
        # generics
        self.name = name
        self.x = x
        self.y = y
        self.icon = icon

        self.ai = ai
        self.block_view = block_view
        self.elevation = elevation
        self.mobile = mobile
        self.size = size
        self.view = view
        self.crew = crew
        self.mast_sail = mast_sail
        self.weapons = weapons
        self.wings = wings
        self.cargo = cargo
        self.sprite_sheet = sprite_sheet

        # components
        if self.ai is not None:
            self.ai.owner = self
        if self.block_view is not None:
            self.block_view.owner = self
        if self.elevation is not None:
            self.elevation.owner = self
        if self.mobile is not None:
            self.mobile.owner = self
        if self.size is not None:
            self.size.owner = self
        if self.view is not None:
            self.view.owner = self
        if self.crew is not None:
            self.crew.owner = self
        if self.mast_sail is not None:
            self.mast_sail.owner = self
        if self.weapons is not None:
            self.weapons.owner = self
        if self.wings is not None:
            self.wings.owner = self
        if self.cargo is not None:
            self.cargo.owner = self
        if self.sprite_sheet is not None:
            self.sprite_sheet.owner = self
