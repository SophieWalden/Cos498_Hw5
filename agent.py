import pygame
import params
import cell_terrain
import random

class Agent:
    def __init__(self, display, image, pos=[0, 2]):
        self.image = pygame.transform.scale(image, (30, 60))
        self.pos = list(pos)

        self.display = display
        self.display_pos = list(pos)

        self.ticks_between_updates = 10
        self.ticks = 0

        self.vy, self.vx = 0, 0
    
    def tick(self, game_map, dt):
        self.ticks += dt

        # Gravity
        if game_map.is_open(self.pos[0], self.pos[1] + 1):
            if 1 > self.vy > -1: self.vy = 1
            self.vy += 0.005 * dt
        else:
            self.vy = 0    

        self.move(int(self.vx), int(self.vy), game_map)
        
        self.vx *= 0.4
        if abs(self.vx) < 1: self.vx = 0


        while self.ticks >= self.ticks_between_updates:
            # Choose move
            if random.random() < 0.2:
                move = random.choice([(-1, 0), (1, 0), (0, 2) if self.vy == 0 else (0, 0)])
                
                if game_map.is_open(self.pos[0] - move[0], self.pos[1] - move[1]):
                    self.vx += -move[0]
                    self.vy += -move[1]
    
            elif random.random() < 0.1:
                move = random.choice([(-1, 0), (1, 0), (0, -1) if random.random() < 0.5 else (0, 0)])

                if game_map.is_breakable(self.pos[0] - move[0], self.pos[1] - move[1]):
                    game_map.break_block(self.pos[0] - move[0], self.pos[1] - move[1])

            
            self.ticks -= self.ticks_between_updates

        if abs(self.pos[0] - self.display_pos[0]) + abs(self.pos[1] - self.display_pos[1]) > 0.1:
            dx, dy = self.pos[0] - self.display_pos[0], self.pos[1] - self.display_pos[1]

            self.display_pos[0] += dx * 0.8
            self.display_pos[1] += dy * 0.8
        else:
            self.display_pos = self.pos[:]

    def move(self, dx, dy, game_map):
        
        
        while dx != 0 and game_map.is_open(self.pos[0] + (dx // abs(dx)), self.pos[1]):
            self.pos[0] += dx // abs(dx)
            
            if dx < 0: dx += 1
            else: dx -= 1
        
        while dy != 0 and game_map.is_open(self.pos[0], self.pos[1] + (dy // abs(dy))):
            self.pos[1] += dy // abs(dy)
            
            if dy < 0: dy += 1
            else: dy -= 1
        