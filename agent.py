import pygame
import params
import cell_terrain
import random
import structure

from collections import defaultdict

class Agent:
    def __init__(self, display, image, pos=[0, 2]):
        self.image = pygame.transform.scale(image, (30, 60))
        self.pos = list(pos)

        self.display = display
        self.display_pos = list(pos)

        self.ticks_between_updates = 30
        self.ticks = 0

        self.inventory = defaultdict(lambda: 0)

        self.vy, self.vx = 0, 0

        self.structure = None
        self.pathing_mode = None

        self.past_locations = []
        self.past_location_count = 30
        self.name = "normal"
    
    def tick(self, game_map, dt):
        self.ticks += dt

        while self.ticks >= self.ticks_between_updates:
            self.agent_logic(game_map)

            self.move(int(self.vx), int(self.vy), game_map)
            
            self.vx *= 0.4
            if abs(self.vx) < 1: self.vx = 0
            
            self.ticks -= self.ticks_between_updates

 
        if abs(self.pos[0] - self.display_pos[0]) + abs(self.pos[1] - self.display_pos[1]) > 0.1:
            dx, dy = self.pos[0] - self.display_pos[0], self.pos[1] - self.display_pos[1]

            self.display_pos[0] += dx * 0.25
            self.display_pos[1] += dy * 0.25

        self.past_locations.append([self.display_pos[0], self.display_pos[1]])
        if len(self.past_locations) > self.past_location_count: self.past_locations.pop(0)

    def build_structure(self, game_map):
        if not self.structure or not self.structure.actions: return
        if len(self.structure.actions[0]) == len(self.structure.actions): 
            dx = -len(self.structure.actions) if len(self.structure.actions) % 2 == 1 else 0
            self.move(dx, -len(self.structure.actions), game_map)
        
        removeIndex = [-1, -1]
        for j, row in enumerate(self.structure.actions):
            for i, tile in enumerate(row):
                goingRight = j % 2 == 0

                self.move([-1, 1][goingRight], 0, game_map) 

                if tile == "air":
                    self.dig_block(0, 0, game_map)
                else:
                    block = random.choice(list(self.inventory.keys()))
                    if tile in self.inventory: block = tile

                    self.place_block(0, 0, block, game_map, random.choice(params.BLOCK_COLORS))
    

                removeIndex = [i, j]

                break
            if removeIndex != [-1, -1]: break
        
        if removeIndex == [-1, -1]:
            self.structure = None
        else:
            self.structure.actions[removeIndex[1]].pop(removeIndex[0])
            if not self.structure.actions[removeIndex[1]]:
                self.move(0, 1, game_map) 
                self.dig_block(0, 0, game_map)


    def agent_logic(self, game_map):
        if self.structure and self.structure.actions:
            self.build_structure(game_map)
        
        elif random.random() < 0.5:
            move = random.choice([(-1, 0), (1, 0), (0, 1), (0, -1)])
        
            self.move(-move[0], -move[1], game_map)
        elif random.random() < 0.4:
            move = random.choice([(-1, 0), (1, 0), (0, -1) if random.random() < 0.5 else (0, 0), (0, 1)])

            if game_map.is_breakable(self.pos[0] - move[0], self.pos[1] - move[1]):
                block = game_map.break_block(self.pos[0] - move[0], self.pos[1] - move[1])

                if block: 
                    self.inventory[block] += 1

        elif random.random() < 0.05:
            structure_name = random.choice(list(structure.STRUCTURE_COSTS.keys()))
            self.structure = structure.Structure(structure_name)
            if not sum(self.inventory.values()) > self.structure.cost["blocks"]:
                self.structure = None
 
        elif self.inventory:
            block = random.choice(list(self.inventory.keys()))
            move = random.choice([(-1, 0), (1, 0), (0, 1)])
            new_pos = self.pos[0] - move[0], self.pos[1] - move[1]

            if game_map.is_open(new_pos[0], new_pos[1]):
                placed = game_map.place(new_pos[0], new_pos[1], block)

                if placed:
                    self.inventory[block] -= 1

                    if self.inventory[block] == 0: 
                        del self.inventory[block]

    def can_move(self, dx, dy, game_map):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        return game_map.is_open(x, y)

    def dig_block(self, dx, dy, game_map):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        if game_map.is_breakable(x, y):
            block = game_map.break_block(x, y)
            if block:
                self.inventory[block] += 1
    
    def place_block(self, dx, dy, block, game_map, color=None):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        if game_map.is_open(x, y) and self.inventory[block] > 0:
            placed = game_map.place(x, y, block, color)
            if placed:
                self.inventory[block] -= 1
                if self.inventory[block] == 0: 
                    del self.inventory[block]

    def try_step_up(self, game_map):
        if not game_map.is_open(self.pos[0], self.pos[1] + 1):
            if not game_map.is_open(self.pos[0], self.pos[1] - 1):
                self.dig_block(0, -1, game_map)
            else:
                self.jump()
        else:
            for block in self.inventory:
                if self.place_block(0, 1, block, game_map):
                    break

    def jump(self):
        if self.vy != 0: return

        self.vy -= 2

    def move(self, dx, dy, game_map):
        
        
        while dx != 0 and game_map.in_bounds(self.pos[0] + dx // abs(dx), self.pos[1]):
            self.pos[0] += dx // abs(dx)
            
            if dx < 0: dx += 1
            else: dx -= 1
        
        while dy != 0  and game_map.in_bounds(self.pos[0], self.pos[1] + dy // abs(dy)): 
            self.pos[1] += dy // abs(dy)
    

            if dy < 0: dy += 1
            else: dy -= 1
        
class CopierAgent(Agent):
    """ Copier Agent Takes Screenshots of its Surrounding and Paste it elsewhere"""
    def __init__(self, display, image, pos=[0, 2]):
        super().__init__(display, image, pos)
        self.screenshot = []
        self.screenshot_size = 10
        self.cost = {}
        self.screenshot_position = [0, 0]
        self.name = "copier"

    def agent_logic(self, game_map):

        if self.structure and self.structure.actions:
            self.build_structure(game_map)
        elif random.random() < 0.5:
            move = random.choice([(-1, 0), (1, 0), (0, 1), (0, -1)])
        
            self.move(-move[0], -move[1], game_map)
        elif random.random() < 0.1:
            move = random.choice([(-1, 0), (1, 0), (0, -1) if random.random() < 0.5 else (0, 0), (0, 1)])

            if game_map.is_breakable(self.pos[0] - move[0], self.pos[1] - move[1]):
                block = game_map.break_block(self.pos[0] - move[0], self.pos[1] - move[1])

                if block: 
                    self.inventory[block] += 1

        elif random.random() < 0.5 and self.screenshot == None:
            self.take_screenshot(game_map)
        
        elif self.screenshot and abs(self.pos[0] - self.screenshot_position[0]) + abs(self.pos[1] - self.screenshot_position[1]) > 15:
            if sum(self.inventory.values()) >= self.cost["blocks"]:
                self.structure = structure.Structure("custom", self.screenshot)
                self.screenshot = None
       
    def take_screenshot(self, game_map):
        self.screenshot = []
        self.cost = {"blocks": 0}
        for j in range(self.screenshot_size):
            self.screenshot.append([])
            for i in range(self.screenshot_size):
                pos = (i + self.pos[0], j + self.pos[1])
                if game_map.in_bounds(pos[0], pos[1]):
                    tile = game_map.tiles[pos[1]][pos[0]]

                    if tile.terrain == cell_terrain.Terrain.Open:
                        self.screenshot[-1].append("air")
                    else:
                        self.screenshot[-1].append(tile.terrain)
                        self.cost["blocks"] += 1
        self.screenshot_position = [pos[0], pos[1]]
