import pygame, os
import params
import cell_terrain
from collections import OrderedDict
import time
from agent import SiphonAgent

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
               cell_terrain.Terrain.Stone: "stone_tile",
               cell_terrain.Terrain.Obsidian: "obsidian_tile",
               cell_terrain.Terrain.Iron: "iron_tile"}

BACKGROUND_TILE_IMAGES = {cell_terrain.Terrain.Stone: "stone_tile_background",
                          cell_terrain.Terrain.Open: "open_tile_background",
                          cell_terrain.Terrain.Dirt: "dirt_tile_background",
                          cell_terrain.Terrain.Grass: "dirt_tile_background",
                          cell_terrain.Terrain.Obsidian: "stone_tile_background",
                          cell_terrain.Terrain.Iron: "stone_tile_background"}

class Display:
    def __init__(self):
        self.camera_pos = [0, 0]
        self.zoom, self.desired_zoom = round(1 * 32) / 32, round(1 * 32) / 32
        self.width, self.height = 1400, 800

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.images = self.load_images()
        self.font = pygame.freetype.Font('JetBrainsMono-Regular.ttf', 18)

        # Caches
        self.image_cache = LRUCache()
        self.painted_block_cache = {}
        self.text_cache = {}

        self.mouse_held_down_since = 0
        self.agent_tracking = 0
        self.tracking_wanted_pos = [0, 0]

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
        locations = {}
        for agent in agents:
            x, y = agent.display_pos
            x, y = self.get_world_coordinates(x, y)
            y -= 30 * self.zoom

            for i, location in enumerate(agent.past_locations[::-1]):
                particleSize = int(40 * (0.9 ** i))
                if particleSize <= 0: continue

                effectSurface = pygame.Surface((particleSize, particleSize))
                color = params.AGENT_COLORS[agent.name]
                effectSurface.fill(params.AGENT_COLORS[agent.name])

                x2, y2 = self.get_world_coordinates(location[0], location[1])
                x2 += 10 * self.zoom
                y2 -= 20 * self.zoom
      
                self.blit(effectSurface, x2, y2, (particleSize, particleSize), f"particle_{particleSize}_{color[0]}_{color[1]}_{color[2]}")

            
            locations[agent] = (x, y)
            self.blit(agent.image, x, y, (60, 60), f"agent_{agent.name}")

        # Drawing siphon beam effect
        for agent in agents:
            if type(agent) == SiphonAgent:
                remove_indexes = []
                for i in range(len(agent.siphon_beam)):
                    agent.siphon_beam[i][1] -= 1
                    starting_location = locations[agent]
                    starting_location = [starting_location[0] + 30 * self.zoom, starting_location[1] + 30 * self.zoom]
                    end_location = locations[agent.siphon_beam[i][0]]
                    end_location = [end_location[0] + 30 * self.zoom, end_location[1] + 30 * self.zoom]
                    pygame.draw.line(self.screen, (140, 70, 0), starting_location, end_location, int(15 * self.zoom))

                    if agent.siphon_beam[i][1] < 0: 
                        remove_indexes.append(i)

                for index in remove_indexes[::-1]:
                    popped_agent, _ = agent.siphon_beam.pop(index)
                    agent.siphoning_agents.remove(popped_agent)
            

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
                
                    position = self.get_world_coordinates(chunk_x, chunk_y, TILE_SIZE * 16)
                    
                    if not chunk.rendered or chunk.render_update:
                        chunk.render_update = False
                        chunk.rendered = self.render_chunk(chunk, board)

                    self.blit(chunk.rendered, position[0], position[1], (TILE_SIZE * 16, TILE_SIZE * 16))

    def render_chunk(self, chunk, board):
        rendered_chunk = pygame.Surface((TILE_SIZE * 16, TILE_SIZE * 16))
        

        for background_tile in chunk.background_tiles:
            
            if background_tile.terrain in BACKGROUND_TILE_IMAGES:
                in_chunk_position = (background_tile.pos[0] % 16, background_tile.pos[1] % 16)
                rendered_chunk.blit(self.images[BACKGROUND_TILE_IMAGES[background_tile.terrain]], (TILE_SIZE * in_chunk_position[0], TILE_SIZE * in_chunk_position[1]))

        for tile in chunk.tiles:
            if tile.terrain in TILE_IMAGES:
                in_chunk_position = (tile.pos[0] % 16, tile.pos[1] % 16)

                image = self.images[TILE_IMAGES[tile.terrain]]
                if tile.color != None:
                    name = f"{tile.terrain}_{tile.color}"

                    if name not in self.painted_block_cache:
                        newImage = image.copy()
                        newImage.fill(tile.color, special_flags=pygame.BLEND_RGBA_MULT)
                        self.painted_block_cache[name] = newImage
                    image = self.painted_block_cache[name]

                rendered_chunk.blit(image, (TILE_SIZE * in_chunk_position[0], TILE_SIZE * in_chunk_position[1]))
 
            elif tile.pos[1] != 0 and board.tiles[tile.pos[1] - 1][tile.pos[0]].terrain != cell_terrain.Terrain.Open:
                surface = pygame.Surface((TILE_SIZE, TILE_SIZE // 4), pygame.SRCALPHA)
                surface.fill((0,0,0, 100))

                rendered_chunk.blit(surface, (TILE_SIZE * in_chunk_position[0], TILE_SIZE * (in_chunk_position[1] + 1)))

        return rendered_chunk
                
    def draw_text(self, given_surface, msg, x, y, color):
        if msg.isdigit():
            surfaces = []
            width, height = 0, 0

            for number in msg:
                surface, rect = self.text_cache[number]
                surfaces.append((surface, rect))
                width += rect[2]
                height = max(height, rect[3])

            width += 2 * len(surfaces)
            text_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            rect_x = 0
            for (surface, rect) in surfaces:
                text_surface.blit(surface, (rect_x, 0))
                rect_x += rect[2] + 2
        else:
            if msg not in self.text_cache:
                surface, rect = self.font.render(msg, color)
                self.text_cache[msg] = (surface, None)

            text_surface = self.text_cache[msg][0]


        given_surface.blit(text_surface, (x, y))

    def draw_ui(self):
        self.draw_text(self.screen, f"Tracking: {self.agent_tracking}", 10, 10, (200, 200, 200))

    def tick(self, board, agents):
        # Dragging
        rel, pressed, pos = pygame.mouse.get_rel(), pygame.mouse.get_pressed(), pygame.mouse.get_pos()
   
        if pressed[0] and self.agent_tracking == None:
            self.camera_pos[0] += -rel[0] * (1 / self.zoom)
            self.camera_pos[1] += -rel[1] * (1 / self.zoom)
        elif self.agent_tracking != None:
            self.tracking_wanted_pos = agents[self.agent_tracking].display_pos[:]
            self.tracking_wanted_pos = [item * TILE_SIZE for item in self.tracking_wanted_pos]
            self.tracking_wanted_pos[0] -= (self.width /self.zoom) // 2
            self.tracking_wanted_pos[1] -= (self.height /self.zoom) // 2


            if pressed[0]: self.agent_tracking = None
   
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

        # Have a slower lerp speed then the units when tracking to make camera less shaky
        if self.agent_tracking != None:

            if abs(self.camera_pos[0] - self.tracking_wanted_pos[0]) + abs(self.camera_pos[1] - self.tracking_wanted_pos[1]) > 0.1:
                dx, dy = self.camera_pos[0] - self.tracking_wanted_pos[0], self.camera_pos[1] - self.tracking_wanted_pos[1]

                self.camera_pos[0] -= dx * 0.05
                self.camera_pos[1] -= dy * 0.05

        self.camera_pos[0] = min(max(self.camera_pos[0], 0), board.width * TILE_SIZE - self.width * 1/self.zoom)
        self.camera_pos[1] = min(max(self.camera_pos[1], 0), board.height * TILE_SIZE - self.height * 1/self.zoom)

        if pressed[0] and self.mouse_held_down_since == 0:
            self.mouse_held_down_since = time.perf_counter()

        if not pressed[0] and self.mouse_held_down_since != 0:
            self.mouse_held_down_since = 0