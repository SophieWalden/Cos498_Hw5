class Cell:
    def __init__(self, terrain, pos):
        self.terrain, self.pos = terrain, pos
        self.displayPos = self.pos[:]
        self.chunk = None