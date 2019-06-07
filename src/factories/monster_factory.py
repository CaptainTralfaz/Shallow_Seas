
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


from random import randint

from random_utils import random_choice_from_dict
from components.size import Size
from components.cargo import ItemCategory, Item, Cargo
from components.view import View
from entity import Entity
from render_functions import RenderOrder
from components.fighter import Fighter
from components.mobile import Mobile


def entity_picker(entity_count: int, travels: int):
    """
    creates dict of entity chances and returns list of entity names
    :param entity_count: int base number of entities per map
    :param travels: int number of times player has changed maps
    :return: list of entity names
    """
    entity_dict = {'chest': 5 + travels,  # provides pearls, food, arrows, other valuables
                   'sunken_ship:': 5 + travels,  # provides wood, canvas, rope, weapons?, ammo?, mines
                   'giant_bat': 20 - travels,
                   'sea_serpent': 25 - travels,
                   'sea_turtle': 20,
                   # 'siren': travels,
                   'wyvern': travels - 10,
                   'octopus': travels - 15,
                   'black_dragon': travels - 20,
                   'kraken': travels - 25,
                   'red_dragon': travels - 30,
                    }
    
    return [random_choice_from_dict(entity_dict) for count in range(entity_count + travels)]
    
    
def generate_entity(name):
    # get entity from json by name
    
    json_data = {"json_data": "values"}
    
    json_name = json_data.get('name')
    json_icon = json_data.get('icon')
    json_render = json_data.get('render_order')
    json_manifest = json_data.get('manifest')
    json_fighter = json_data.get('fighter')
    json_size = json_data.get('size')
    json_ai = json_data.get('ai')
    json_mobile = json_data.get('mobile')
    json_view = json_data.get('view')

    size_component = None
    if json_size:
        size_component = Size(json_size)
    
    cargo_component = None
    if json_manifest:
        manifest = []
        for item in json_manifest:
            manifest.append(Item(name=item.get('name'),
                                 icon=item.get('icon'),
                                 category=ItemCategory(item.get('category')),
                                 weight=item.get('weight'),
                                 volume=item.get('volume'),
                                 quantity=randint(10, 20) + randint(10, 20)))
        cargo_component = Cargo(max_volume=5, max_weight=10, manifest=manifest)
    
    fighter_component = None
    if json_fighter == 'hull':
        fighter_component = Fighter(name=json_fighter, max_hps=int(json_size) * 10 + 5)
    elif json_fighter == 'body':
        fighter_component = Fighter(name=json_fighter, max_hps=int(json_size) * 8 + 4 + randint(-size_component - 1,
                                                                                                size_component + 1))
    view_component = None
    if json_view is not None:
        view_component = View(view=size_component + 3 + json_view)

    mobile_component = None
    if json_mobile:
        mobile_component = Mobile(direction=randint(0, 5), max_momentum=json_size.value * 2 + 2)

    entity = Entity(name=json_name,
                    x=0, y=0,
                    icon=json_icon,
                    render_order=RenderOrder(json_render),
                    size=size_component,
                    view=view_component,
                    fighter=fighter_component,
                    ai=json_ai,
                    mobile=mobile_component,
                    cargo=cargo_component)

    return entity


def generate_cargo():
    data = None

    with open('../data/items.yaml', 'r') as stream:

        try:
            data = load(stream, Loader=Loader)
        except FileNotFoundError:
            print("Load Error!")
        
    item = 'Turtle Shell'
    thing = Item(name=item,
                 weight=data[item]['weight'],
                 volume=data[item]['volume'],
                 icon=data[item]['icon'],
                 category=data[item]['category'])

    print(thing.name)
    print(thing.weight)
    print(thing.volume)
    print(thing.icon)
    print(thing.category)
    print(thing.quantity)
    
    
if __name__ == '__main__':
    generate_cargo()
