class Entity:
    """
    A generic object to represent ships, enemies, terrain, etc.
    """
    
    def __init__(self, name, x, y, icon, ai=None, block_view=None, elevation=None, mobile=None,
                 size=None, view=None, crew=None, mast_sail=None, weapons=None, weapon_slots=None, wings=None,
                 cargo=None, sprite_sheet=None):
        # generics
        self.name = name
        self.x = x
        self.y = y
        self.icon = icon
        
        # components
        if ai is not None:
            self.ai = ai
            self.ai.owner = self
        if block_view is not None:
            self.block_view = block_view
            self.block_view.owner = self
        if elevation is not None:
            self.elevation = elevation
            self.elevation.owner = self
        if mobile is not None:
            self.mobile = mobile
            self.mobile.owner = self
        if size is not None:
            self.size = size
            self.size.owner = self
        if view is not None:
            self.view = view
            self.view.owner = self
        if crew is not None:
            self.crew = crew
            self.crew.owner = self
        if mast_sail is not None:
            self.mast_sail = mast_sail
            self.mast_sail.owner = self
        if weapons is not None:
            self.weapons = weapons
            self.weapons.owner = self
        if weapon_slots is not None:
            self.weapon_slots = weapon_slots
            self.weapon_slots.owner = self
        if wings is not None:
            self.wings = wings
            self.wings.owner = self
        if cargo is not None:
            self.cargo = cargo
            self.cargo.owner = self
        if sprite_sheet is not None:
            self.sprite_sheet = sprite_sheet
            self.sprite_sheet.owner = self
