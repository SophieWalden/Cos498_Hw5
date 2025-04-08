import pygame, os
import params
import cell_terrain
from collections import OrderedDict
import time

TILE_SIZE = params.TILE_SIZE

class LRUCache:
    def __init__(self, max_size=250):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key) 
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False) 
        self.cache[key] = value
        return value

TILE_IMAGES = {cell_terrain.Terrain.Dirt: "dirt_tile",
               cell_terrain.Terrain.Grass: "grass_tile",
               cell_terrain.Terrain.Stone: "stone_tile"}

BACKGROUND_TILE_IMAGES = {cell_terrain.Terrain.Stone: "stone_tile_background",
                          cell_terrain.Terrain.Open: "open_tile_background",
                          cell_terrain.Terrain.Dirt: "dirt_tile_background",
                          cell_terrain.Terrain.Grass: "dirt_tile_background"}

class Display:
    def __init__(self):
        self.camera_pos = [0, 0]
        self.zoom, self.desired_zoom = round(1 * 32) / 32, round(1 * 32) / 32
        self.width, self.height = 1400, 800

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.images = self.load_images()

        # Caches
        self.image_cache = LRUCache()
        self.text_cache = {}

        self.mouse_held_down_since = 0

    def load_images(self):
        images = {}
        for filename in os.listdir("images"):
            full_path = f"images/{filename}"
            key = filename[:filename.index(".")]

            images[key] = pygame.image.load(full_path).convert_alpha()

        return images
    

    def fill(self, color):
        self.screen.fill(color)

    def blit(self, image, x, y, size, name=None):
        if not self.is_onscreen(x, y, size): return False

        if not name:
            self.screen.blit(pygame.transform.scale(image, (size[0] * self.zoom, size[1] * self.zoom)), (x, y))
            return True
        
        adjusted_image = self.image_cache.get((name, self.zoom))

        if adjusted_image == None:
            adjusted_image = self.image_cache.put((name, self.zoom), pygame.transform.scale(image, (size[0] * self.zoom, size[1] * self.zoom)))

        self.screen.blit(adjusted_image, (x, y))
        return True

    def get_world_coordinates(self, x, y, size=TILE_SIZE):
        x, y = x * size, y * size

        x -= self.camera_pos[0]
        y -= self.camera_pos[1]

        x *= self.zoom
        y *= self.zoom

        return x, y
    
    def is_onscreen(self, x, y, size):
        return x > -size[0] * self.zoom and x < self.width and y > -size[1] * self.zoom and y < self.height
    
    def draw_agents(self, agents):
        for agent in agents:
            x, y = agent.display_pos
            x, y = self.get_world_coordinates(x, y)
            y -= 30 * self.zoom

            self.blit(agent.image, x, y, (30, 60), "agent")

    def draw_map(self, board):
        top_left_chunk = (self.camera_pos[0] // (TILE_SIZE * 16), self.camera_pos[1] // (TILE_SIZE * 16))
        right_bottom_chunk = ((self.camera_pos[0] + self.width * 1/self.zoom) // (TILE_SIZE * 16), (self.camera_pos[1] + self.height * 1/self.zoom) // (TILE_SIZE * 16))
        top_left_chunk = [int(item) for item in top_left_chunk]
        right_bottom_chunk = [int(item) for item in right_bottom_chunk]

        for chunk_x in range(top_left_chunk[0], right_bottom_chunk[0] + 1):
            for chunk_y in range(top_left_chunk[1], right_bottom_chunk[1] + 1):
                chunk_coords = (chunk_x, chunk_y)

                if chunk_coords in board.chunks:
                    chunk = board.chunks[chunk_coords]

                    for background_tile in chunk.background_tiles:
                        x, y = self.get_world_coordinates(background_tile.pos[0], background_tile.pos[1], TILE_SIZE)
                        background_tile.displayPos = (x, y)
                        
                        if background_tile.terrain in BACKGROUND_TILE_IMAGES:
                            self.blit(self.images[BACKGROUND_TILE_IMAGES[background_tile.terrain]], x, y, (TILE_SIZE, TILE_SIZE), f"{background_tile.terrain}_background")

                    for tile in chunk.tiles:
                        x, y = self.get_world_coordinates(tile.pos[0], tile.pos[1], TILE_SIZE)
                        tile.displayPos = (x, y)
                        
                        if tile.terrain != cell_terrain.Terrain.Open:
                            self.blit(self.images[TILE_IMAGES[tile.terrain]], x, y, (TILE_SIZE, TILE_SIZE), str(tile.terrain))
                        elif tile.pos[1] != 0 and board.tiles[tile.pos[1] - 1][tile.pos[0]].terrain != cell_terrain.Terrain.Open:
                            surface = pygame.Surface((TILE_SIZE, TILE_SIZE // 4), pygame.SRCALPHA)
                            surface.fill((0,0,0, 100))

                            self.blit(surface, x, y, (TILE_SIZE, TILE_SIZE // 4), "top_block_shading")
          

                
                

    def tick(self, board):
        # Dragging
        rel, pressed, pos = pygame.mouse.get_rel(), pygame.mouse.get_pressed(), pygame.mouse.get_pos()
   
        if pressed[0]:
            self.camera_pos[0] += -rel[0] * (1 / self.zoom)
            self.camera_pos[1] += -rel[1] * (1 / self.zoom)
   
        # Zooming
        if abs(self.zoom - self.desired_zoom) > 0.005:
            mx, my = pos
            world_x_before = (mx / self.zoom) + self.camera_pos[0]
            world_y_before = (my / self.zoom) + self.camera_pos[1]

            self.zoom += (self.desired_zoom - self.zoom) * 1
            self.zoom = max(min(self.zoom, 2.5), 0.5)

            world_x_after = (mx / self.zoom) + self.camera_pos[0]
            world_y_after = (my / self.zoom) + self.camera_pos[1]

            self.camera_pos[0] += world_x_before - world_x_after
            self.camera_pos[1] += world_y_before - world_y_after
        else:
            self.zoom = self.desired_zoom

        self.camera_pos[0] = min(max(self.camera_pos[0], 0), board.width * TILE_SIZE - self.width * 1/self.zoom)
        self.camera_pos[1] = min(max(self.camera_pos[1], 0), board.height * TILE_SIZE - self.height * 1/self.zoom)

        if pressed[0] and self.mouse_held_down_since == 0:
            self.mouse_held_down_since = time.perf_counter()

        if not pressed[0] and self.mouse_held_down_since != 0:
            self.mouse_held_down_since = 0