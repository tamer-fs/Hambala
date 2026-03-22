import pygame
import random
import time
import numpy
import math

from func import *

from scripts.bow import *

# gebouw ideeen
# snelle schutters toren
# healing tower die je geneest als je in buurt staat
# iets met porcupine spikes


class DefenceBuildings:
    def __init__(self, grid_x, grid_y, building_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.absolute_x = grid_x * 16
        self.absolute_y = grid_y * 16
        self.building_type = building_type  # types: "Bow"
        self.absolute_x = self.grid_x * 16 + 8
        self.absolute_y = self.grid_y * 16 + 8
        self.bow = False

        if self.building_type == "Bow":
            self.bow = Bow(size=42, unlimited_arrows=True)
            self.charge_started = False
            self.charge_timer_set = False
            self.charge_delay_timer = -1
            self.charge_delay = 3  # 2-5
            self.bow_shoot_timer = -1
            self.bow_shoot_delay = 4  # 0-6
            self.max_shooting_range = 400
            self.max_shoot_delay = 4
            self.damage_multiplier = 1

        if self.building_type == "Fast Bow":
            self.bow = Bow(size=38, unlimited_arrows=True)
            self.charge_started = False
            self.charge_timer_set = False
            self.charge_delay_timer = -1
            self.charge_delay = 0  # 2-5
            self.bow_shoot_timer = -1
            self.bow_shoot_delay = 2  # 0-6
            self.max_shooting_range = 200
            self.max_shoot_delay = 2
            self.damage_multiplier = 0.5

        if self.building_type == "Sniper Bow":
            self.bow = Bow(size=48, unlimited_arrows=True)
            self.charge_started = False
            self.charge_timer_set = False
            self.charge_delay_timer = -1
            self.charge_delay = 6  # 2-5
            self.bow_shoot_timer = -1
            self.bow_shoot_delay = 6  # 0-6
            self.max_shooting_range = 600
            self.max_shoot_delay = 6
            self.damage_multiplier = 1.5

    def draw(self, screen, scrollx, scrolly):
        if self.bow:
            self.bow.draw(screen, scrollx, scrolly)

    def bow_update(self, dt, enemies):
        angle = 20
        if len(enemies) > 0:
            # enemy uitkiezen
            distances = []
            for enemy in enemies:
                distances.append(
                    get_distance(
                        self.absolute_x,
                        self.absolute_y,
                        enemy["rect"].x,
                        enemy["rect"].y,
                    )
                )
            closest_enemy = enemies[distances.index(min(distances))]

            if min(distances) < self.max_shooting_range:

                # boog mikken
                enemy_x, enemy_y = closest_enemy["rect"].x, closest_enemy["rect"].y
                player_dx = enemy_x - self.absolute_x
                player_dy = enemy_y - self.absolute_y
                player_dx = 0.01 if player_dx == 0 else player_dx
                player_dy = 0.01 if player_dy == 0 else player_dy
                tan_angle = player_dy / player_dx
                angle = math.degrees(math.atan(tan_angle))
                if abs(player_dx) != player_dx:
                    angle += 180

                # boog schieten
                if self.charge_started == False:
                    if self.charge_timer_set == False:
                        self.charge_delay_timer = time.perf_counter()
                        self.charge_timer_set = True
                    if (
                        time.perf_counter() - self.charge_delay_timer
                        > self.charge_delay
                    ):
                        self.bow.start_charge()
                        self.charge_started = True
                        self.bow_shoot_timer = time.perf_counter()

                if (
                    time.perf_counter() - self.bow_shoot_timer > self.bow_shoot_delay
                    and self.charge_started == True
                ):
                    self.bow.shoot_arrow(0)
                    self.charge_started = False
                    self.bow_shoot_delay = self.max_shoot_delay

                    self.charge_timer_set = False

        self.bow.update(self.absolute_x, self.absolute_y, round(angle), dt)

    def update(self, dt, enemies):
        if self.bow:
            self.bow_update(dt, enemies)
