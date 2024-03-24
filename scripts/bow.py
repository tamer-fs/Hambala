import pygame
import random
import time
import numpy

from func import *

class Bow:
    def __init__(self, unlimited_arrows=False):
        self.bow_frames = {}
        for angle in range(0, 360):
            self.bow_frames[angle] = []
            for x in range(0, 4):
                photo = pygame.image.load(f"assets/bow/bow{str(x) if x != 0 else ''}.png")
                photo = pygame.transform.rotate(photo, -angle)
                self.bow_frames[angle].append(photo)

        self.arrow_list = []
        self.bow_rect = self.bow_frames[0][0].get_rect(center=(0,0))
        self.x = 0
        self.y = 0 
        self.direction = 0
        self.charging = False
        self.charge = 0 # from 1 to 3 (including 3)
        self.charge_cooldown = 1
        self.charge_timer = -1
        self.arrows = "ul" if unlimited_arrows else 100
        
    def update(self, x, y, direction):
        self.x = x
        self.y = y  
        self.width = self.bow_frames[self.direction][self.charge].get_width()
        self.height = self.bow_frames[self.direction][self.charge].get_height()

        self.bow_rect.x = self.x - (self.width / 2)
        self.bow_rect.y = self.y - (self.height / 2)
        
        self.direction = direction % 360

        if self.charging:
            # print(f"arrow charge: {self.charge}")      
            if time.perf_counter() - self.charge_timer > self.charge_cooldown:
                self.charge_timer = time.perf_counter()
                if self.charge < 3:
                    self.charge += 1

        for arrow in self.arrow_list:
            arrow.update()
          
    def start_charge(self):
        self.charging = True
                
    def shoot_arrow(self):
        self.arrow_list.append(Arrow(self.direction, self.charge, self.x, self.y))
        
        self.charging = False
        self.charge = 0
        if self.arrows != "ul":
            self.arrows -= 1
    
    def draw(self, screen):
        screen.blit(self.bow_frames[self.direction][self.charge], self.bow_rect)
        for arrow in self.arrow_list:
            arrow.draw(screen)

class Arrow:
    def __init__(self, angle, charge, x, y):
        self.angle = angle
        self.charge = charge
        self.dx = numpy.cos(numpy.radians(self.angle))
        self.dy = numpy.sin(numpy.radians(self.angle))
        self.vx = 10
        self.vy = 0
        self.arrow_img = pygame.transform.rotate(pygame.image.load("assets/bow/arrow.png"), self.angle)
        self.rect = self.arrow_img.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.arrow_img, self.rect)

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        