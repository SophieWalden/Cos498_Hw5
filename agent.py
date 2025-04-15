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
    
    def tick(self, game_map, dt):
        self.ticks += dt

        


        while self.ticks >= self.ticks_between_updates:

            if self.structure and self.structure.actions:
                action, pos = self.structure.actions.pop(0)
                if action == "move":
                    self.move(pos[0], pos[1], game_map) 
                elif action == "break":
                    self.dig_block(0, 0, game_map)
                elif action == "place":
                    block = random.choice(list(self.inventory.keys()))
                    self.place_block(0, 0, block, game_map)
            
            elif random.random() < 0.5:
                move = random.choice([(-1, 0), (1, 0), (0, 1), (0, -1)])
            
                self.move(-move[0], -move[1], game_map)
            elif random.random() < 0.3:
                move = random.choice([(-1, 0), (1, 0), (0, -1) if random.random() < 0.5 else (0, 0), (0, 1)])

                if game_map.is_breakable(self.pos[0] - move[0], self.pos[1] - move[1]):
                    block = game_map.break_block(self.pos[0] - move[0], self.pos[1] - move[1])

                    if block: 
                        self.inventory[block] += 1

            elif random.random() < 0.02:
                self.structure = structure.Structure("spiral")
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



            self.move(int(self.vx), int(self.vy), game_map)
            
            self.vx *= 0.4
            if abs(self.vx) < 1: self.vx = 0
            
            self.ticks -= self.ticks_between_updates

 
        if abs(self.pos[0] - self.display_pos[0]) + abs(self.pos[1] - self.display_pos[1]) > 0.1:
            dx, dy = self.pos[0] - self.display_pos[0], self.pos[1] - self.display_pos[1]

            self.display_pos[0] += dx * 0.8
            self.display_pos[1] += dy * 0.8


    def can_move(self, dx, dy, game_map):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        return game_map.is_open(x, y)

    def dig_block(self, dx, dy, game_map):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        if game_map.is_breakable(x, y):
            block = game_map.break_block(x, y)
            if block:
                self.inventory[block] += 1
    
    def place_block(self, dx, dy, block, game_map):
        x, y = self.pos[0] + dx, self.pos[1] + dy
        if game_map.is_open(x, y) and self.inventory[block] > 0:
            placed = game_map.place(x, y, block)
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
        