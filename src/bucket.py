class Bucket:
    def __init__(self, size):
        self.size = size
        self.current = 0
    
    def fill(self, amount):
        self.current += amount
        if self.current > self.size:
            self.current -= self.size + 1
            return 1
        elif self.current < 0:
            self.current += self.size + 1
            return -1
        else:
            return 0


class Container:
    def __init__(self, size):
        self.size = size
        self.current = 0
    
    def fill(self, amount):
        if self.current + amount > self.size:
            self.current = self.size
        elif self.current + amount < 0:
            self.current = 0
        else:
            self.current += amount
