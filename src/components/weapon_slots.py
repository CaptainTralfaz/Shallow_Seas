from src.components.weapon import Weapon


class WeaponSlots:
    def __init__(self, size):
        self.bow = None
        self.port = None
        self.stern = None
        self.starboard = None
        
        if size == 0:
            self.bow = []
            self.port = []
            self.stern = []
            self.starboard = []
            
        if size == 1:
            self.bow = []
            self.port = [0]
            self.stern = []
            self.starboard = [0]

        if size == 2:
            self.bow = []
            self.port = [0, 0]
            self.stern = [0]
            self.starboard = [0, 0]

        if size == 3:
            self.bow = [0]
            self.port = [0, 0, 0]
            self.stern = [0]
            self.starboard = [0, 0, 0]

        if size == 4:
            self.bow = [0, 0]
            self.port = [0, 0, 0, 0]
            self.stern = [0, 0]
            self.starboard = [0, 0, 0, 0]

    def add_all(self):
        for slot in range(len(self.bow)):
            self.bow[slot] = Weapon("Ballista", 1, 4, 5, 3, cool_down=2)
            print(slot, self.bow)
        for slot in range(len(self.port)):
            self.port[slot] = Weapon("Ballista", 1, 4, 5, 3, cool_down=2)
            print(slot, self.port)
        for slot in range(len(self.stern)):
            self.stern[slot] = Weapon("Ballista", 1, 4, 5, 3, cool_down=2)
            print(slot, self.stern)
        for slot in range(len(self.starboard)):
            self.starboard[slot] = Weapon("Ballista", 1, 4, 5, 3, cool_down=2)
            print(slot, self.starboard)
