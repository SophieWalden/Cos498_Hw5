import sys, time
import params

import pygame
from pygame.locals import *
import game_map
import display
import cell_terrain
from agent import Agent, CopierAgent, GravityAgent, SiphonAgent, PaintAgents
import random 
pygame.init()

class Game:
    def __init__(self, display=None):
        self.display = display
        self.fpsClock = pygame.time.Clock()

        self.board = game_map.GameMap()
        self.reset = False
        self.agents = []

        
        agent_classes = {"normal": Agent, "copier": CopierAgent, "gravity": GravityAgent, "siphon": SiphonAgent, "painter": PaintAgents}
        for agent, count in params.AGENT_COUNTS.items():
            for _ in range(count):
                created_agent = agent_classes[agent](self.display, self.display.images[params.AGENT_IMAGES[agent]], (random.randint(10, int(self.board.width * 0.7)), self.board.height // 2))
                self.agents.append(created_agent)

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
                elif event.key == pygame.K_DOWN:
                    if self.display.agent_tracking == None: self.display.agent_tracking = 0
                    if self.display.agent_tracking == 0: self.display.agent_tracking = len(self.agents) - 1
                    else: self.display.agent_tracking -= 1
                elif event.key == pygame.K_UP:
                    if self.display.agent_tracking == None: self.display.agent_tracking = 0
                    if self.display.agent_tracking == len(self.agents) - 1: self.display.agent_tracking = 0
                    else: self.display.agent_tracking += 1

    def agent_updates(self, dt):
        for agent in self.agents:
            agent.tick(self.board, dt * self.speed, self.agents)


    def draw(self):
        self.display.fill("#121212")
        self.display.draw_map(self.board)
        self.display.tick(self.board, self.agents)

        self.display.draw_agents(self.agents)
        
        self.display.draw_ui()

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