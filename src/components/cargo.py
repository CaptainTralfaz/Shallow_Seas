from enum import Enum


class Cargo:
    def __init__(self, max_volume, max_weight, manifest):
        """
        Holds maximum weight and volume of a container, and a list of Items currently held
        TODO: make over-weight effect ship's momentum value
        TODO: make over-weight effect targeted features (higher water line = lower chance for hull to be hit)
        TODO: make over-volume items can be washed overboard in storm, or hit in combat
        :param max_volume: int maximum volume available in ship's cargo hold
        :param max_weight: int maximum weight a ship can SAFELY carry
        :param manifest: list of Items TODO: change this to a dict
        """
        self.max_volume = max_volume
        self.max_weight = max_weight
        self.manifest = manifest
    
    def to_json(self):
        return {
            'max_volume': self.max_volume,
            'max_weight': self.max_weight,
            'manifest': [item.to_json() for item in self.manifest]
        }
    
    @staticmethod
    def from_json(json_data):
        max_volume = json_data.get('max_volume')
        max_weight = json_data.get('max_weight')
        manifest = [Item.from_json(item) for item in json_data.get('manifest')]
        
        return Cargo(max_volume=max_volume, max_weight=max_weight, manifest=manifest)
    
    @property
    def weight(self):
        """
        Determines total weight of cargo in manifest
        :return: total weight of cargo in manifest
        """
        weight = 0
        for item in self.manifest:
            weight += item.weight * item.quantity
        return weight
    
    @property
    def volume(self):
        """
        Determines total volume of cargo in manifest
        :return: total volume of cargo in manifest
        """
        volume = 0
        for item in self.manifest:
            volume += item.volume * item.quantity
        return volume
    
    def add_item_to_manifest(self, item, message_log):
        """
        Add a new item to the manifest
        :param item: Item object to be added
        :param message_log: game message log
        :return: None - modifies manifest directly
        """
        manifest_names = [cargo.name for cargo in self.manifest]
        if item.name not in manifest_names:
            message_log.add_message(message='{} {} added to cargo'.format(item.quantity, item.name))
            self.manifest.append(item)
            item.owner = self
        else:
            for cargo in self.manifest:
                if cargo.name == item.name:
                    adjust_quantity(self, item=cargo, amount=item.quantity, message_log=message_log)
    
    def remove_item_from_manifest(self, item, message_log):
        """
        Removes an item from the manifest
        :param item: Item object to be removed
        :param message_log: game message log
        :return: None - modifies manifest directly
        """
        if item in self.manifest:
            self.manifest.remove(item)
            message_log.add_message(message="removed {} from manifest".format(item.name))
        else:
            message_log.add_message(message="not carrying any {}".format(item.name))


class Item:
    def __init__(self, name: str, icon: str, category, weight: float, volume: float, quantity: int = 1):
        """
        Object holding an Item
        :param name: str name of the object
        :param icon: str name for the icon of the object
        :param category: category of the item TODO: actually use this for sorting on the manifest display
        :param weight: float weight of each individual item
        :param volume: float volume of each individual item
        :param quantity: int number of items
        """
        self.name = name
        self.weight = weight * 1.0
        self.volume = volume * 1.0
        self.icon = icon
        self.category = category
        self.quantity = quantity

    def to_json(self):
        """
        Serialize Item object to json
        :return: json representation of Item object
        """
        return {
            'name': self.name,
            'weight': self.weight,
            'volume': self.volume,
            'quantity': self.quantity,
            'icon': self.icon,
            'category': self.category.value
        }
    
    @staticmethod
    def from_json(json_data):
        """
        Deserialize Item object from json
        :param json_data: json representation of Item object
        :return: Item Object
        """
        name = json_data.get('name')
        weight = json_data.get('weight')
        volume = json_data.get('volume')
        quantity = json_data.get('quantity')
        icon = json_data.get('icon')
        category = json_data.get('category')
        
        return Item(name=name, weight=weight, volume=volume, quantity=quantity, icon=icon,
                    category=ItemCategory(category))
    
    def get_item_weight(self):
        """
        Determines the total weight of an Item
        :return: float total weight of Item
        """
        return self.weight * self.quantity
    
    def get_item_volume(self):
        """
        Determines the total volume of an Item
        :return: float total volume of Item
        """
        return self.volume * self.quantity


def adjust_quantity(cargo, item, amount, message_log):
    """
    Add or subtract quantity of an Item
    :param cargo: cargo object
    :param item: name of Item object
    :param amount: amount to modify quantity by
    :param message_log: game message log
    :return: None - modify Item quantity directly
    """
    item.quantity += amount
    if amount > 0:
        message_log.add_message('{} {} added to cargo'.format(amount, item.name))
    elif amount < 0 < amount + item.quantity:
        message_log.add_message('{} {} removed from cargo'.format(abs(amount), item.name))
    elif amount < 0 and (amount + item.quantity == 0):
        message_log.add_message('All {} {} removed from cargo'.format(abs(amount), item.name))
        cargo.remove_item_from_manifest(item=item, message_log=message_log)


class ItemCategory(Enum):
    """
    Category type of item for sorting
    """
    MATERIALS = 0
    GOODS = 1
    SUPPLIES = 2
    EXOTICS = 3
    ARMAMENTS = 4
