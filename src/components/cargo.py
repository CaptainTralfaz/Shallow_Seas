from enum import Enum


class Cargo:
    def __init__(self, capacity, manifest):
        self.capacity = capacity
        self.manifest = manifest

    def get_manifest_weight(self):
        weight = 0
        for item in self.manifest:
            weight += item.weight * item.quantity
        return weight

    def get_manifest_volume(self):
        volume = 0
        for item in self.manifest:
            volume += item.volume * item.quantity
        return volume
    
    def add_item_to_manifest(self, item):
        manifest_names = [cargo.name for cargo in self.manifest]
        if item.name not in manifest_names:
            self.manifest.append(item)
        else:
            for cargo in self.manifest:
                if cargo.name == item.name:
                    cargo.adjust_quantity(item.quantity)
    
    def remove_item_from_manifest(self, item):
        if item in self.manifest:
            self.manifest.remove(item)
            print("removed " + item.name + "from manifest")
        else:
            print("not carrying any " + item.name)


class Item:
    def __init__(self, name, icon, category, weight, volume, quantity=0):
        self.name = name
        self.weight = weight / 1.0
        self.volume = volume / 1.0
        self.quantity = quantity
        self.icon = icon
        self.category = category

    def get_item_weight(self):
        return self.weight * self.quantity
    
    def get_item_volume(self):
        return self.volume * self.quantity

    def adjust_quantity(self, amount):
        self.quantity += amount
        # if self.quantity < 0:


class ItemCategory(Enum):
    MATERIALS = 0
    GOODS = 1
    SUPPLIES = 2
    EXOTICS = 3
    ARMAMENTS = 4
