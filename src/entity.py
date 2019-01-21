from enum import Enum

from components.ai import ai_from_json
from components.size import Size
from render_functions import RenderOrder


class Entity:
    """
    A generic object to represent ships, enemies, containers, etc.
    """
    
    def __init__(self, name: str, x: int, y: int, icon: str, render_order: Enum = RenderOrder.CORPSE, ai=None,
                 block_view=None, mobile=None, size=None, view=None, crew=None, mast_sail=None, weapons=None,
                 wings=None, cargo=None, sprite_sheet: str = None, fighter=None):
        """
        Initialize Entity object
        :param name: str name of the object
        :param x: int x location
        :param y: int y location
        :param icon: str name of icon
        :param render_order: enum render order
        :param ai: object AI component
        :param block_view: boolean
        :param mobile: object Mobile component
        :param size: enum Size component
        :param view: object View component
        :param crew: object Crew component
        :param mast_sail: object Masts component
        :param weapons: object WeaponsList component
        :param wings: object Wings component
        :param cargo: object Cargo component
        :param sprite_sheet: string name of SpriteSheet component  # Not used yet
        :param fighter: object Fighter component
        """
        # generics
        self.name = name
        self.x = x
        self.y = y
        self.icon = icon
        self.render_order = render_order
        
        self.ai = ai
        self.block_view = block_view
        self.mobile = mobile
        self.size = size
        self.view = view
        self.crew = crew
        self.mast_sail = mast_sail
        self.weapons = weapons
        self.wings = wings
        self.cargo = cargo
        self.sprite_sheet = sprite_sheet
        self.fighter = fighter
        
        # components
        if self.ai is not None:
            self.ai.owner = self
        if self.block_view is not None:
            self.block_view.owner = self
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
        if self.fighter is not None:
            self.fighter.owner = self
    
    def to_json(self):
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'icon': self.icon,
            'render_order': self.render_order.value,
            'ai': self.ai if self.ai else None,
            'block_view': self.block_view if self.block_view else None,
            'mobile': self.mobile if self.mobile else None,
            'size': self.size.value if self.size else None,
            'view': self.view.view if self.view else None,
            'crew': self.crew if self.crew else None,
            'mast_sail': self.mast_sail if self.mast_sail else None,
            'weapons': self.weapons if self.weapons else None,
            'wings': self.wings if self.wings else None,
            'cargo': self.cargo if self.cargo else None,
            'sprite_sheet': self.sprite_sheet if self.sprite_sheet else None,
            'fighter': self.fighter if self.fighter else None
        }
    
    @staticmethod
    def from_json(json_data):
        name = json_data.get('name')
        x = json_data.get('x')
        y = json_data.get('y')
        icon = json_data.get('icon')
        render_order = json_data.get('render_order')
        ai = json_data.get('ai')
        block_view = json_data.get('block_view')
        mobile = json_data.get('mobile')
        size = json_data.get('size')
        view = json_data.get('view')
        crew = json_data.get('crew')
        mast_sail = json_data.get('mast_sail')
        weapons = json_data.get('weapons')
        wings = json_data.get('wings')
        cargo = json_data.get('cargo')
        sprite_sheet = json_data.get('sprite_sheet')
        fighter = json_data.get('fighter')
        
        return Entity(name, x, y, icon, render_order=RenderOrder(render_order), ai=ai_from_json(ai),
                      block_view=block_view, mobile=mobile, size=Size(size), view=view, crew=crew, mast_sail=mast_sail,
                      weapons=weapons, wings=wings, cargo=cargo, sprite_sheet=None, fighter=fighter)
