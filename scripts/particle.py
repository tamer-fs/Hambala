import pygame
import random
import time
import math

##############################
#         Walk Particle      #
##############################


class WalkParticle:
    def __init__(self, x, y):
        self.width = 6.3
        self.height = 6.3
        self.x, self.y = x, y
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        vx_vy = [0.5, 0.3, 0.1, -0.1, -0.3, -0.5]
        self.vx = random.choice(vx_vy)
        self.vy = random.choice(vx_vy)
        self.delete_timer = time.perf_counter()
        self.player_tile = (0, 0)
        self.color = "orange"

    def draw(self, screen):
        if int(self.width) < 5:
            pygame.draw.ellipse(screen, self.color, self.rect)

    def update(self, scrollx, scrolly, deltaT, player, world):
        self.x += self.vx * deltaT / 10
        self.y += self.vy * deltaT / 10
        self.width -= 0.015 * deltaT
        self.height -= 0.015 * deltaT
        self.rect = pygame.Rect(
            (int(self.x) - scrollx, int(self.y) - scrolly),
            (int(self.width), int(self.height)),
        )
        self.player_tile = (math.floor(player.x / 16), math.floor(player.y / 16))
        if world[self.player_tile[1], self.player_tile[0]] in [5, 6, 7]:
            self.color = (159, 127, 86)
        else:
            self.color = (100, 124, 68)


##############################
#         Hit Particle       #
##############################


class HitParticle:
    def __init__(self, x, y, color="red", up=False):
        self.width = 6.3
        self.height = 6.3
        self.x, self.y = x, y
        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        self.up = up
        # vx_vy = [0.5, 0.3, 0.1, -0.1, -0.3, -0.5]
        # self.vx = random.choice(vx_vy)
        # self.vy = random.choice(vx_vy)

        self.vx = random.uniform(-0.7, 0.7)
        if self.up:
            self.vy = random.uniform(-0.2, -0.1)     
            self.vx = random.uniform(-0.1, 0.1) 
        else:
            self.vy = random.uniform(-0.7, 0.7)

        self.delete_timer = time.perf_counter()
        self.player_tile = (0, 0)
        self.color = color

    def draw(self, screen):
        if int(self.width) < 5:
            pygame.draw.ellipse(screen, self.color, self.rect)

    def update(self, scrollx, scrolly, deltaT, player, world):
        self.x += self.vx * deltaT / 10
        self.y += self.vy * deltaT / 10
            
        self.width -= 0.015 * deltaT
        self.height -= 0.015 * deltaT
        self.rect = pygame.Rect(
            (int(self.x) - scrollx, int(self.y) - scrolly),
            (int(self.width), int(self.height)),
        )
