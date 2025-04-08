import cell_terrain
import random
from cell import Cell

class GameMap:
    def __init__(self):
        self.width, self.height = 500, 120
        self.tiles, self.background_tiles, self.chunks = self.generate_board(self.width, self.height)

    def is_open(self, x, y):
        return x > 0 and x < len(self.tiles[0]) and y > 0 and y < len(self.tiles) and self.tiles[y][x].terrain in [cell_terrain.Terrain.Open, cell_terrain.Terrain.Water]

    def is_breakable(self, x, y):
        return x > 0 and x < len(self.tiles[0]) and y > 0 and y < len(self.tiles) and self.tiles[y][x].terrain not in [cell_terrain.Terrain.Open, cell_terrain.Terrain.Water]

    def break_block(self, x, y):
        self.tiles[y][x].terrain = cell_terrain.Terrain.Open

    def generate_board(self, width, height):
        board = [[0] * width for _ in range(height)]
        background_board = [[0] * width for _ in range(height)]
        chunks = {}
        
        previous_column = None

        for i in range(len(board[0])):
            if not previous_column:
                grass_level = random.randint(20, 30)
                stone_level = grass_level + 10

                previous_column = [grass_level, stone_level]
            else:
                grass_level, stone_level = previous_column

                grass_level += random.randint(-1, 1)

                stone_level = grass_level + 10


                previous_column = [grass_level, stone_level]

            for j in range(len(board)):
                terrain = cell_terrain.Terrain.Open

                if j == grass_level:
                    terrain = cell_terrain.Terrain.Grass

                if j > grass_level:
                    terrain = cell_terrain.Terrain.Dirt
                
                if j > stone_level:
                    terrain = cell_terrain.Terrain.Stone

                board[j][i] = Cell(terrain, (i, j))
                background_board[j][i] = Cell(terrain, (i, j))

                chunk_cord = (i // 16, j // 16)
                if chunk_cord not in chunks:
                    chunks[chunk_cord] = Chunk()
                
                chunks[chunk_cord].add_tile(board[j][i])
                chunks[chunk_cord].add_background_tile(background_board[j][i])

        return board, background_board, chunks
    
class Chunk:
    def __init__(self, size=16):
        self.tiles, self.size = [], size
        self.background_tiles = []

    def add_tile(self, cell):
        self.tiles.append(cell)
    
    def add_background_tile(self, cell):
        self.background_tiles.append(cell)