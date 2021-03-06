from enum import Enum

from components.ai import ai_from_json
from components.cargo import Cargo
from components.crew import Crew
from components.fighter import Fighter
from components.masts import Masts
from components.mobile import Mobile
from components.size import Size
from components.view import View
from components.weapon import WeaponList
from components.wings import Wings
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
            'ai': self.ai.get_ai_name() if self.ai else None,
            'block_view': self.block_view.to_json() if self.block_view else None,
            'size': self.size.value if self.size is not None else None,
            'view': self.view.view if self.view is not None else None,
            'fighter': self.fighter.to_json() if self.fighter else None,
            'mobile': self.mobile.to_json() if self.mobile else None,
            'mast_sail': self.mast_sail.to_json() if self.mast_sail else None,
            'weapons': self.weapons.to_json() if self.weapons else None,
            'wings': self.wings.to_json() if self.wings else None,
            'crew': self.crew.to_json() if self.crew is not None else None,
            'cargo': self.cargo.to_json() if self.cargo else None
            # 'sprite_sheet': self.sprite_sheet if self.sprite_sheet else None,
        }
    
    @staticmethod
    def from_json(json_data):
        name = json_data.get('name')
        x = json_data.get('x')
        y = json_data.get('y')
        icon = json_data.get('icon')
        render_order = RenderOrder(json_data.get('render_order'))
        ai = ai_from_json(json_data.get('ai'))  # if json_data.get('ai') else None
        block_view = json_data.get('block_view') if json_data.get('block_view') is not None else None
        mobile = Mobile.from_json(json_data.get('mobile')) if json_data.get('mobile') is not None else None
        size = Size(json_data.get('size')) if json_data.get('size') is not None else None
        view = View(json_data.get('view')) if json_data.get('view') is not None else None
        crew = Crew.from_json(json_data.get('crew')) if json_data.get('crew') is not None else None
        mast_sail = Masts.from_json(json_data.get('mast_sail')) if json_data.get('mast_sail') is not None else None
        weapons = WeaponList.from_json(json_data.get('weapons')) if json_data.get('weapons') is not None else None
        wings = Wings.from_json(json_data.get('wings')) if json_data.get('wings') is not None else None
        cargo = Cargo.from_json(json_data.get('cargo')) if json_data.get('cargo') is not None else None
        #        sprite_sheet = json_data.get('sprite_sheet')
        fighter = Fighter.from_json(json_data.get('fighter')) if json_data.get('fighter') is not None else None
        
        return Entity(name, x, y, icon, render_order=RenderOrder(render_order), ai=ai,
                      block_view=block_view, mobile=mobile, size=size, view=view, crew=crew, mast_sail=mast_sail,
                      weapons=weapons, wings=wings, cargo=cargo, fighter=fighter)

    def damage_location(self, can_hit_locations: list):
        location_list = {}
        if self.fighter and self.fighter.name in can_hit_locations:
            location_list['fighter'] = 50
        if self.mast_sail:
            if 'mast' in can_hit_locations:
                location_list['mast'] = 10
            if 'sail' in can_hit_locations:
                location_list['sail'] = 15
        if self.wings and 'wings' in can_hit_locations:
            location_list['wings'] = 25
        if self.crew and 'crew' in can_hit_locations:
            location_list['crew'] = 15
        if self.weapons and 'weapons' in can_hit_locations:
            location_list['weapons'] = 15
        if self.cargo and 'cargo' in can_hit_locations and self.cargo.volume > self.cargo.max_volume:
            # Over volume max, cargo can be hit
            location_list['cargo'] = self.cargo.volume - self.cargo.max_volume
            if self.cargo.weight > self.cargo.max_weight and self.fighter:
                # Over weight max, fighter component gets hit less
                location_list['fighter'] = 50 - (self.cargo.weight - self.cargo.max_weight)

