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
        if item not in self.manifest:
            self.manifest.append(item)
            print("already carrying " + item.name)
        else:
            print(item.name + " added")
    
    def remove_item_from_manifest(self, item):
        if item in self.manifest:
            self.manifest.remove(item)
            print("removed " + item.name + "from manifest")
        else:
            print("not carrying any " + item.name)


class Item:
    def __init__(self, name, icon, weight, volume, quantity=0):
        self.name = name
        self.weight = weight
        self.volume = volume
        self.quantity = quantity
        self.icon = icon

    def get_item_weight(self):
        return self.weight * self.quantity
    
    def get_item_volume(self):
        return self.volume * self.quantity

    def adjust_quantity(self, amount):
        self.quantity += amount
        # if self.quantity < 0:

