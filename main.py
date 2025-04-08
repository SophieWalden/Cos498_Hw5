import sys, time
import params

import pygame
from pygame.locals import *
import game_map
import display
import cell_terrain
from agent import Agent
import random 
pygame.init()

class Game:
    def __init__(self, display=None):
        self.display = display
        self.fpsClock = pygame.time.Clock()

        self.board = game_map.GameMap()
        self.reset = False
        self.agents = [Agent(self.display, self.display.images["agent_sprite"], (random.randint(10, int(self.board.width * 0.9)), 5)) for _ in range(100)]
        self.speed = 1

    def event_handling(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                self.display.width, self.display.height = event.w, event.h
                self.display.screen = pygame.display.set_mode((event.w, event.h),
                                            pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_val = min(max(event.y, -3), 3)/6 + 1
                self.display.desired_zoom = max(min(scroll_val * self.display.desired_zoom, 2.5), 0.5)
                self.display.desired_zoom = round(self.display.desired_zoom * 32) / 32

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset = True
                elif event.key == pygame.K_LEFT:
                    self.speed = max(self.speed // 2, 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.speed = min(self.speed * 2, 1024)


    def agent_updates(self, dt):
        for agent in self.agents:
            agent.tick(self.board, dt * self.speed)


    def draw(self):
        self.display.fill("#121212")
        self.display.draw_map(self.board)
        self.display.tick(self.board)

        self.display.draw_agents(self.agents)

        pygame.display.flip()

    def main_loop(self):
        dt = 1/100000
        while not self.reset:
            self.event_handling()
            self.draw()
            self.agent_updates(dt)
            dt = self.fpsClock.tick(params.FPS)
      

import cProfile, pstats

if __name__ == "__main__":
    display = display.Display()

    while True:
        # profiler = cProfile.Profile()
        # profiler.enable()

        Game(display).main_loop()

        # profiler.disable()
        # stats = pstats.Stats(profiler).sort_stats("tottime")
        # stats.print_stats(30)