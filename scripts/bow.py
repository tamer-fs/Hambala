import pygame
import random
import time

from func import *

class Bow:
    def __init__(self, unlimited_arrows):
        self.bow_frames = [pygame.image.load(), pygame.image.load(), pygame.image.load()]
        self.bow_img = pygame.image.load()
        self.bow_rect = self.bow_img.get_rect(center=(0,0))
        self.x = 0
        self.y = 0 
        self.direction = 0
        self.charge = 0
        self.charge_timer = -1
        self.arrows = "ul" if unlimited_arrows else 0
        
    def update(self, x, y, direction):
        self.x = x
        self.y = y  
        self.bow_rect.x = self.x
        self.bow_rect.y = self.y  
        for index, frame in enumerate(self.bow_frames):
            self.bow_frames[index] = pygame.transform.rotate(frame, direction)
        
    def shoot(self):
        print("arrow shot")
        
    def shoot_arrow(self):
                
                
        
    def draw(self, screen):
        screen.blit(self.bow_img, self.bow_rect)