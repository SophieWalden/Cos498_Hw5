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

        self.aptitudes = {"clutter_removal": random.random(), 
                          "pathfinder": random.random(),
                          "edge_seeker": random.random()}
        self.break_radius = 2
        self.last_move = [0, 0]
    
    def tick(self, game_map, dt, agents):
        self.ticks += dt

        while self.ticks >= self.ticks_between_updates:
            self.agent_logic(game_map, agents)

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

    def build_structure(self, game_map, color_enabled = True):
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
                elif self.inventory:
                    block = random.choice(list(self.inventory.keys()))
                    if tile in self.inventory: block = tile


                    retVal = self.place_block(0, 0, block, game_map)


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


    def agent_logic(self, game_map, _):
        if self.structure and self.structure.actions:
            self.build_structure(game_map)
        
        elif random.random() < 0.5:
            move = random.choice([(-1, 0), (1, 0), (0, 1), (0, -1)])
        
            self.move(-move[0], -move[1], game_map)
        elif random.random() < 0.1:
            self.aptitude_break_block(game_map)
        elif random.random() < 0.005:
            structure_name = random.choice(list(structure.STRUCTURE_COSTS.keys()))
            self.structure = structure.Structure(structure_name)
            if not sum(self.inventory.values()) > self.structure.cost["blocks"]:
                self.structure = None
 
    def aptitude_break_block(self, game_map):
        """ Each Agent is unique. Some hate block piles, some hate loose blocks. This determines which block they break in their radius based on their aptitudes """

        break_block_pattern = random.choices(list(self.aptitudes.keys()), weights=list(self.aptitudes.values()))[0]

        if break_block_pattern == "pathfinder": # Breaks based on where the agent is moving
            self.dig_block(self.last_move[0], self.last_move[1], game_map)
        
        elif break_block_pattern == "edge_seeker": # Prioritizes blocks with 2 or 3 neighbors
            block_to_break = [0, 0]
            max_neighbors = -1

            search_offsets = sorted([(i, j) for j in range(-2, 3) for i in range(-2, 3)],key=lambda pos: abs(pos[0]) + abs(pos[1]))
            cardinal_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for dx, dy in search_offsets:
                x, y = self.pos[0] + dx, self.pos[1] + dy
                if not game_map.is_breakable(x, y):
                    continue

                neighbors = 0
                for nx, ny in cardinal_offsets:
                    if game_map.is_breakable(x + nx, y + ny):
                        neighbors += 1
                    if neighbors > 3:
                        break 

                if neighbors > max_neighbors:
                    max_neighbors = neighbors
                    block_to_break = (dx, dy)
                    if neighbors == 3:
                        break

            self.dig_block(block_to_break[0], block_to_break[1], game_map)
                        

        elif break_block_pattern == "clutter_removal": # Prioritizes blocks with least neighbors
            block_to_break = [0, 0]
            max_neighbors = -1

            search_offsets = sorted([(i, j) for j in range(-2, 3) for i in range(-2, 3)],key=lambda pos: abs(pos[0]) + abs(pos[1]))
            cardinal_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for dx, dy in search_offsets:
                x, y = self.pos[0] + dx, self.pos[1] + dy
                if not game_map.is_breakable(x, y):
                    continue

                neighbors = 0
                for nx, ny in cardinal_offsets:
                    if game_map.is_breakable(x + nx, y + ny):
                        break
                else:
                    block_to_break = (dx, dy)
                    break

            self.dig_block(block_to_break[0], block_to_break[1], game_map)


    
    
    def can_move(self, dx, dy, game_map):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        return game_map.is_open(x, y)

    def dig_block(self, dx, dy, game_map):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        if game_map.is_breakable(x, y):
            block = game_map.break_block(x, y)
            if block:
                self.inventory[block] += 1
            return block
        
        return False
    
    def place_block(self, dx, dy, block, game_map, color=None):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        if not game_map.is_open(x, y): return False

        if self.inventory[block] > 0:
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
        
        move = [0, 0]
        while dx != 0 and game_map.in_bounds(self.pos[0] + dx // abs(dx), self.pos[1]):
            self.pos[0] += dx // abs(dx)
            move[0] += dx // abs(dx)

            if dx < 0: dx += 1
            else: dx -= 1
        
        while dy != 0  and game_map.in_bounds(self.pos[0], self.pos[1] + dy // abs(dy)): 
            self.pos[1] += dy // abs(dy)
            move[1] += dy // abs(dy)

            if dy < 0: dy += 1
            else: dy -= 1

        if move != [0, 0]: self.last_move = move
        
class CopierAgent(Agent):
    """ Copier Agent Takes Screenshots of its Surrounding and Paste it elsewhere"""
    def __init__(self, display, image, pos=[0, 2]):
        super().__init__(display, image, pos)
        self.screenshot = None
        self.screenshot_size = 10
        self.cost = {}
        self.screenshot_position = [0, 0]
        self.name = "copier"

    def agent_logic(self, game_map, _):

        if self.structure and self.structure.actions:
            self.build_structure(game_map, color_enabled=False)
        elif random.random() < 0.5:
            move = random.choice([(-1, 0), (1, 0), (0, 1), (0, -1)])
        
            self.move(-move[0], -move[1], game_map)

        elif random.random() < 0.1:
            self.aptitude_break_block(game_map)

        elif random.random() < 0.5 and (random.random() < 0.05 or self.screenshot == None):
            self.take_screenshot(game_map)
        
        elif self.screenshot and abs(self.pos[0] - self.screenshot_position[0]) + abs(self.pos[1] - self.screenshot_position[1]) > 100:
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

class GravityAgent(Agent):
    """ The world is absent of natural gravity, it requires a lifeless orb to do it for them"""
    def __init__(self, display, image, pos):
        super().__init__(display, image, pos)
        self.name = "gravity"

    def agent_logic(self, game_map, _):
        if game_map.is_breakable(self.pos[0], self.pos[1]) and game_map.is_open(self.pos[0], self.pos[1] + 1):
            block = self.dig_block(0, 0, game_map)
            self.place_block(0, 1, block, game_map)
        else:
            move = random.choice([(-1, 0), (1, 0), (0, 1), (0, -1)])
            self.move(-move[0], -move[1], game_map)

class SiphonAgent(Agent):
    """ Sometimes the agents steal too many blocks, lets keep them in check and return them to the world """
    def __init__(self, display, image, pos):
        super().__init__(display, image, pos)
        self.name = "siphon"
        self.siphon_beam = []
        self.siphoning_agents = set([])

    def dist(self, p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) **.5

    def agent_logic(self, game_map, agents):

        if sum(self.inventory.values()) < 300:
            for agent in agents:
                if agent == self: continue
                if type(agent) == SiphonAgent or type(agent) == GravityAgent: continue
                if self.dist(self.pos, agent.pos) > 50: continue
                if sum(agent.inventory.values()) < 100: continue
                if agent in self.siphoning_agents: continue

                for key, val in agent.inventory.items():
                    self.inventory[key] += val
                
                agent.inventory = defaultdict(lambda: 0)
                self.siphon_beam.append([agent, 15])
                self.siphoning_agents.add(agent)

        if self.inventory and game_map.is_open(self.pos[0], self.pos[1]):
            block = random.choice(list(self.inventory.keys()))
            self.place_block(0, 0, block, game_map)
        else:
            move = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.move(-move[0], -move[1], game_map)


class PaintAgents(Agent):
    """ Why wake the world from a beautiful dream when the waking world is all so drab
            The painter simply adds a little more color into the existing world  
    """
    def __init__(self, display, image, pos):
        super().__init__(display, image, pos)
        self.name = "painter"
      

    def agent_logic(self, game_map, agents):

        if game_map.is_not_painted(self.pos[0], self.pos[1]):
            block = self.dig_block(0, 0, game_map)
            block_color = random.choice(params.BLOCK_COLORS)
            self.place_block(0, 0, block, game_map, block_color)
        else:
            move = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.move(-move[0], -move[1], game_map)
