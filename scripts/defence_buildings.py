import pygame
import random
import time
import numpy
import math

from func import *


class DefenceBuildings:
    def __init__(self, grid_x, grid_y, building_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.building_type = building_type  # types: "Bow"
        self.bow = None  # als toren Bow is, dan is dit het boog object

    def draw(self, screen):
        pass

    def update(self, dt):
        pass
