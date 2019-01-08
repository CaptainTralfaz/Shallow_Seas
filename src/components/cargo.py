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
        :param manifest: list of Items
        """
        self.max_volume = max_volume
        self.max_weight = max_weight
        self.manifest = manifest
    
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
        else:
            for cargo in self.manifest:
                if cargo.name == item.name:
                    adjust_quantity(cargo=cargo, amount=item.quantity, message_log=message_log)
    
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
    def __init__(self, name, icon, category, weight, volume, quantity=0):
        """
        Object holding an Item
        :param name: str name of the object
        :param icon: icon of the object
        :param category: category of the item TODO: actually use this for sorting on the manifest display
        :param weight: float weight of each individual item
        :param volume: float volume of each individual item
        :param quantity: int number of items
        """
        self.name = name
        self.weight = weight / 1.0
        self.volume = volume / 1.0
        self.quantity = quantity
        self.icon = icon
        self.category = category
    
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


def adjust_quantity(cargo, amount, message_log):
    """
    Add or subtract quantity of an Item
    :param cargo: Item object
    :param amount: amount to modify quantity by
    :param message_log: game message log
    :return: None - modify Item quantity directly
    """
    cargo.quantity += amount
    if amount > 0:
        message_log.add_message('{} of {} added to cargo'.format(amount, cargo.name))
    elif amount < 0 < amount + cargo.quantity:
        message_log.add_message('{} of {} removed from cargo'.format(abs(amount), cargo.name))
    elif amount < 0 and (amount + cargo.quantity == 0):
        message_log.add_message('All {} of {} removed from cargo'.format(abs(amount), cargo.name))
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
