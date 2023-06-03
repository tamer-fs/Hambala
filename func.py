import math

import pygame
import numpy
import random
import os
import time
import matplotlib
import json

pygame.mixer.init()

def get_distance(x1, y1, x2, y2):
    c2 = math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2)
    c = math.sqrt(c2)
    return c

class Player:
    def __init__(self, images, x, y):
        self.x = x
        self.y = y

        self.images = images
        self.speed = 0.10
        self.idle_frames = ["idle1", "idle2", "idle3", "idle4", "idle5", "idle6"]
        self.idle_frame = 0
        self.walk_frames = ["walk1", "walk2", "walk3", "walk4", "walk5", "walk6"]
        self.walk_frame = 0
        self.run_frames = ["run1", "run2"]
        self.run_frame = 0
        self.update_frame = -1
        self.state = "idle"
        self.direction = "RIGHT"  # direction with RIGHT or LEFT
        self.direction_xy = "UP"  # direction with RIGHT LEFT UP DOWN
        self.energy_value = 100
        self.food_value = 10000
        self.health_value = 10
        self.tomato_feeding = 1000
        self.cookie_feeding = 2500
        self.flower_power = 40
        self.player_tile = (0, 0)
        self.interact_img = pygame.image.load("assets/icons/Interact.png").convert_alpha()
        self.font = pygame.font.Font("assets/Font/SpaceMono-Bold.ttf", 25)
        self.on_interact = False
        self.interact_message = ""
        self.screen_size = pygame.display.get_window_size()
        self.interact_rect = pygame.Rect(self.screen_size[0] / 2 - 200, 15, 400, 40)
        self.interact_render = None
        self.interact_render_rect = None
        self.inter_w, self.inter_h = 0, 0
        self.inventory = None
        self.sword_img_1 = pygame.image.load("assets/tools/Sword-1.png").convert_alpha()
        self.sword_img_1 = pygame.transform.rotate(self.sword_img_1, -45)
        self.sword_img_2 = pygame.image.load("assets/tools/Sword-2.png").convert_alpha()
        self.sword_img_2 = pygame.transform.rotate(self.sword_img_2, -80)
        self.sword_img_3 = pygame.image.load("assets/tools/Sword-3.png").convert_alpha()
        self.sword_img_3 = pygame.transform.rotate(self.sword_img_3, -110)

        self.pickaxe_img_1 = pygame.image.load("assets/tools/pickaxe.png").convert_alpha()
        self.pickaxe_img_2 = pygame.transform.rotate(self.pickaxe_img_1, -45)

        self.pickaxe_img_2_flipped = pygame.transform.flip(self.pickaxe_img_2, True, False)
        self.pickaxe_img_1_flipped = pygame.transform.flip(self.pickaxe_img_1, True, False)
        self.pickaxe_frame = 0
        self.pickaxe_list = [self.pickaxe_img_1, self.pickaxe_img_2]
        self.pickaxe_list_flip = [self.pickaxe_img_1_flipped, self.pickaxe_img_2_flipped]
        self.pickaxe_cooldown = 0

        self.axe_img_1 = pygame.image.load("assets/tools/axe.png").convert_alpha()
        self.axe_img_2 = pygame.transform.rotate(self.axe_img_1, 45)

        self.axe_img_2_flipped = pygame.transform.flip(self.axe_img_2, True, False)
        self.axe_img_1_flipped = pygame.transform.flip(self.axe_img_1, True, False)
        self.axe_frame = 0
        self.axe_list = [self.axe_img_1, self.axe_img_2]
        self.axe_list_flip = [self.axe_img_1_flipped, self.axe_img_2_flipped]
        self.axe_cooldown = 0

        self.sword_img_1_flip = pygame.transform.flip(self.sword_img_1, True, False)
        self.sword_img_2_flip = pygame.transform.flip(self.sword_img_2, True, False)
        self.sword_img_3_flip = pygame.transform.flip(self.sword_img_3, True, False)
        self.sword_update = 0

        self.sword_list = [self.sword_img_1, self.sword_img_2, self.sword_img_3]
        self.sword_list_flipped = [self.sword_img_1_flip, self.sword_img_2_flip, self.sword_img_3_flip]
        self.sword_frame = 0
        self.framed = 0
        self.attacking = False
        self.can_attack = True
        self.sword_selected = False
        self.hitting = False
        self.attack_delay = 0.8
        self.update_frame_1 = 0
        self.cooldown = 0
        self.stone_rect = pygame.Rect((self.screen_size[0] / 2 - 100, 100), (200, 30))
        self.stone_rect2 = pygame.Rect((self.screen_size[0] / 2 - 100, 100), (200, 30))
        self.stone_rect3 = pygame.Rect((self.screen_size[0] / 2 - 108, 100 - 8), (216, 46))

        self.sword_sweep_sound = pygame.mixer.Sound("assets/sounds/sword_swoosh.wav")
        self.damage_sound = pygame.mixer.Sound("assets/sounds/damage.wav")
        self.damaging = False

    def set_window_size(self, screen):
        self.screen_size = screen.get_size()

    def walking(self, keys, deltaT, mouse):
        self.state = "idle"

        if keys[pygame.K_LSHIFT] and self.energy_value > 0 and (
                keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_w]):
            if self.energy_value > 0.025 * deltaT:
                self.speed = 0.525
                self.state = "run"
            self.energy_value -= 0.025 * deltaT
        elif keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_w]:
            self.speed = 0.1
            self.state = "walk"
            if self.energy_value < 100:
                self.energy_value += 0.01 * deltaT
        else:
            if self.energy_value < 100:
                self.energy_value += 0.02 * deltaT

        if self.attacking and self.framed < 3:
            if time.perf_counter() - self.sword_update > 0.0855:
                self.sword_update = time.perf_counter()
                self.sword_frame = (self.sword_frame + 1) % 3
                self.framed += 1
        else:
            self.attacking = False
            self.hitting = False

        if self.can_attack and self.sword_selected \
                and not self.attacking \
                and not self.inventory.holding_item \
                and not self.inventory.hovering_menu:
            if mouse[0] and self.energy_value > 15:
                self.attacking = True
                self.hitting = True
                self.framed = 0
                self.sword_frame = 0
                self.energy_value -= 15
                self.food_value -= 10
                pygame.mixer.Sound.play(self.sword_sweep_sound)

        if keys[pygame.K_d] and keys[pygame.K_w]:
            self.x += 100 * self.speed / numpy.sqrt(200)
            self.y -= 100 * self.speed / numpy.sqrt(200)
            self.direction = "RIGHT"
            self.direction_xy = "RIGHT"

        elif keys[pygame.K_d] and keys[pygame.K_s]:
            self.x += 100 * self.speed / numpy.sqrt(200)
            self.y += 100 * self.speed / numpy.sqrt(200)
            self.direction = "RIGHT"
            self.direction_xy = "RIGHT"

        elif keys[pygame.K_w] and keys[pygame.K_a]:
            self.x -= 100 * self.speed / numpy.sqrt(200)
            self.y -= 100 * self.speed / numpy.sqrt(200)
            self.direction = "LEFT"
            self.direction_xy = "LEFT"

        elif keys[pygame.K_s] and keys[pygame.K_a]:
            self.x -= 100 * self.speed / numpy.sqrt(200)
            self.y += 100 * self.speed / numpy.sqrt(200)
            self.direction = "LEFT"
            self.direction_xy = "LEFT"

        else:
            if keys[pygame.K_d]:
                self.x += 10 * self.speed
                if self.state != "run": self.state = "walk"
                self.direction = "RIGHT"
                self.direction_xy = "RIGHT"

            if keys[pygame.K_a]:
                self.x -= 10 * self.speed
                if self.state != "run": self.state = "walk"
                self.direction = "LEFT"
                self.direction_xy = "LEFT"

            if keys[pygame.K_s]:
                self.y += 10 * self.speed
                if self.state != "run": self.state = "walk"
                self.direction_xy = "DOWN"

            if keys[pygame.K_w]:
                self.y -= 10 * self.speed
                if self.state != "run": self.state = "walk"
                self.direction_xy = "UP"

        if time.perf_counter() - self.update_frame > 0.0825:
            self.update_frame = time.perf_counter()
            if self.state == "idle":
                self.idle_frame = (self.idle_frame + 1) % 6
            elif self.state == "walk":
                self.walk_frame = (self.walk_frame + 1) % 6
            elif self.state == "run":
                self.run_frame = (self.run_frame + 1) % 2

        if self.food_value > 0:
            if self.state == "idle":
                self.food_value -= 0.01 * deltaT
            elif self.state == "walk":
                self.food_value -= 0.010 * deltaT
            elif self.state == "run":
                self.food_value -= 0.02 * deltaT

    def draw(self, screen, scrollx, scrolly):
        scr_w, scr_h = screen.get_size()

        if self.sword_selected:
            if self.direction == "RIGHT" or self.direction_xy == "RIGHT":
                screen.blit(self.sword_list[self.sword_frame], (self.x - 1 - scrollx + 35, self.y - 1 - scrolly + 5))
            if self.direction == "LEFT" or self.direction_xy == "LEFT":
                screen.blit(self.sword_list_flipped[self.sword_frame],
                            (self.x - 1 - scrollx + 12 - 30, self.y - 1 - scrolly + 5))

        if self.inventory.holding_pickaxe:
            if self.direction == "RIGHT" or self.direction_xy == "RIGHT":
                screen.blit(self.pickaxe_list[self.pickaxe_frame],
                            (self.x - 1 - scrollx + 35, self.y - 1 - scrolly + 5))
            if self.direction == "LEFT" or self.direction_xy == "LEFT":
                screen.blit(self.pickaxe_list_flip[self.pickaxe_frame],
                            (self.x - 1 - scrollx + 20 - 30, self.y - 1 - scrolly + 5))

        if self.inventory.holding_axe:
            if self.direction == "RIGHT" or self.direction_xy == "RIGHT":
                screen.blit(self.axe_list_flip[self.axe_frame], (self.x - 1 - scrollx + 35, self.y - 1 - scrolly + 5))
            if self.direction == "LEFT" or self.direction_xy == "LEFT":
                screen.blit(self.axe_list[self.axe_frame], (self.x - 1 - scrollx + 20 - 30, self.y - 1 - scrolly + 5))

        if self.direction == "RIGHT":
            screen.blit(self.images[eval(f"self.{self.state}_frames[self.{self.state}_frame]")],
                        (int(self.x) - scrollx, int(self.y) - scrolly))
        elif self.direction == "LEFT":
            screen.blit(self.images[eval(f"self.{self.state}_frames[self.{self.state}_frame]") + '_flipped'],
                        (int(self.x) - scrollx, int(self.y) - scrolly))

        if self.on_interact:
            screen.blit(self.interact_img, (self.x - 1 - scrollx + 12, self.y - 1 - scrolly - 20))
            # pygame.draw.rect(screen, pygame.Color("#212529"), self.interact_rect, border_radius=15)
            screen.blit(self.interact_render, ((scr_w - self.inter_w) / 2, 15))

    def get_inventory(self, inventory):
        self.inventory = inventory

    def update(self, plants, keys, screen):
        self.player_tile = (int(self.x / 16), int(self.y / 16))

        if self.damaging:
            pygame.mixer.Sound.play(self.damage_sound)
            self.damaging = False

        if plants[self.player_tile[1] + 1, self.player_tile[0] + 1] in [127, 11, 10, 61]:
            self.on_interact = True
            plant = plants[self.player_tile[1] + 1, self.player_tile[0] + 1]
            if plant == 127:
                self.interact_message = "Harvest tomato"
            elif plant == 11:
                self.interact_message = "Harvest flower"
            elif plant == 10:
                self.interact_message = "Mine stone (only with pickaxe)"
            elif plant == 61:
                self.interact_message = "Cut down tree (only with axe)"
            text_w, text_h = self.font.size(self.interact_message)
            self.interact_render = pygame.Surface((text_w + 15, text_h + 15), pygame.SRCALPHA)
            self.inter_w, self.inter_h = self.interact_render.get_size()
            text_render = self.font.render(self.interact_message, True, (255, 255, 255))
            pygame.draw.rect(self.interact_render, pygame.Color("#212529"), ((0, 0), (text_w + 15, text_h + 15)),
                             border_radius=15)
            self.interact_render.blit(text_render, (
            (self.inter_w - text_render.get_width()) / 2, (self.inter_h - text_render.get_height()) / 2))

            self.interact_render.set_alpha(200)

            # self.interact_render_rect = self.interact_render.get_rect(center=(0, 0))
            # self.interact_render_rect = self.interact_render.get_rect(center=(self.interact_rect.x + self.interact_rect.x / 2 - textw / 2 + 50, self.interact_rect.y + 19))
        else:
            self.on_interact = False

        if self.on_interact and self.interact_message == "Harvest tomato" and keys[
            pygame.K_e] and self.inventory.can_fill:
            plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 125
            self.inventory.add_item("tomato ")
        if self.on_interact and self.interact_message == "Harvest flower" and keys[
            pygame.K_e] and self.inventory.can_fill:
            plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 12
            self.inventory.add_item("flower ")
        if self.on_interact \
                and self.interact_message == "Mine stone (only with pickaxe)" \
                and self.inventory.holding_pickaxe:
            pygame.draw.rect(screen, pygame.Color("#212529"), self.stone_rect3, border_radius=26)
            pygame.draw.rect(screen, pygame.Color("#c1121f"), self.stone_rect2, border_radius=20)
            pygame.draw.rect(screen, pygame.Color("#0ead69"), self.stone_rect, border_radius=20)
            if keys[pygame.K_e]:
                if time.perf_counter() - self.cooldown > 0.8:
                    self.stone_rect.width -= (self.screen_size[0] / 4) / 4
                    self.cooldown = time.perf_counter()

                if time.perf_counter() - self.pickaxe_cooldown > 0.5:
                    self.pickaxe_frame = (self.pickaxe_frame + 1) % 2
                    self.pickaxe_cooldown = time.perf_counter()

            elif not keys[pygame.K_e]:
                self.stone_rect = pygame.Rect((self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                                              (self.screen_size[0] / 4 - 16, 30))
                self.stone_rect2 = pygame.Rect((self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                                               (self.screen_size[0] / 4 - 16, 30))
                self.stone_rect3 = pygame.Rect((self.screen_size[0] / 2 - self.screen_size[0] / 8, 100 - 8),
                                               (self.screen_size[0] / 4, 46))
                self.pickaxe_frame = 0
            if self.stone_rect.width <= 0:
                plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 12
                self.inventory.add_item("stone ")
                self.pickaxe_frame = 0

        if self.on_interact and self.interact_message == "Cut down tree (only with axe)" and self.inventory.holding_axe:
            pygame.draw.rect(screen, pygame.Color("#212529"), self.stone_rect3, border_radius=26)
            pygame.draw.rect(screen, pygame.Color("#c1121f"), self.stone_rect2, border_radius=20)
            pygame.draw.rect(screen, pygame.Color("#0ead69"), self.stone_rect, border_radius=20)
            if keys[pygame.K_e]:
                if time.perf_counter() - self.cooldown > 0.8:
                    self.stone_rect.width -= (self.screen_size[0] / 4) / 4
                    self.cooldown = time.perf_counter()

                if time.perf_counter() - self.axe_cooldown > 0.5:
                    self.axe_frame = (self.axe_frame + 1) % 2
                    self.axe_cooldown = time.perf_counter()

            elif not keys[pygame.K_e]:
                self.stone_rect = pygame.Rect((self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                                              (self.screen_size[0] / 4 - 16, 30))
                self.stone_rect2 = pygame.Rect((self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                                               (self.screen_size[0] / 4 - 16, 30))
                self.stone_rect3 = pygame.Rect((self.screen_size[0] / 2 - self.screen_size[0] / 8, 100 - 8),
                                               (self.screen_size[0] / 4, 46))
                self.axe_frame = 0
            if self.stone_rect.width <= 0:
                plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 12
                plants[self.player_tile[1] + 1, self.player_tile[0] + 2] = 12
                plants[self.player_tile[1], self.player_tile[0] + 2] = 12
                plants[self.player_tile[1], self.player_tile[0] + 1] = 12
                self.inventory.add_item("log ")
                self.inventory.add_item("log ")
                self.axe_frame = 0

        if self.food_value <= 0:
            if time.perf_counter() - self.update_frame_1 > 5:
                self.update_frame_1 = time.perf_counter()
                self.health_value -= 0.5
                self.damaging = True

        if time.perf_counter() - self.update_frame_1 > 5 and self.food_value > 800 and self.health_value < 10:
            self.update_frame_1 = time.perf_counter()
            self.health_value += 0.25


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
        self.rect = pygame.Rect((int(self.x) - scrollx, int(self.y) - scrolly), (int(self.width), int(self.height)))
        self.player_tile = (math.floor(player.x / 16), math.floor(player.y / 16))
        if world[self.player_tile[1], self.player_tile[0]] in [5, 6, 7]:
            self.color = (159, 127, 86)
        else:
            self.color = (100, 124, 68)


class ValueBar:
    def __init__(self, pos, size, margin, max_value):
        self.background = pygame.Rect(pos, size)
        self.foreground = pygame.Rect((pos[0] + margin / 2, pos[1] + margin / 2), (size[0] - margin, size[1] - margin))
        self.shadow = pygame.Rect((pos[0] + margin / 2, pos[1] + margin / 2), (size[0] - margin, size[1] - margin))
        self.value = 0
        self.max_value = max_value
        self.width = self.foreground.w
        self.pos = pos

    def draw(self, screen, bg_color, shadow_color, fg_color, icon, padding, radius):
        pygame.draw.rect(screen, bg_color, self.background, border_radius=radius)
        pygame.draw.rect(screen, shadow_color, self.shadow, border_radius=radius - 2)
        pygame.draw.rect(screen, fg_color, self.foreground, border_radius=radius - 2)
        screen.blit(icon, (self.pos[0] + padding[0], self.pos[1] + padding[1]))

    def reset(self, pos, size, margin):
        self.pos = pos
        self.background = pygame.Rect(pos, size)
        self.foreground = pygame.Rect((pos[0] + margin / 2, pos[1] + margin / 2), (size[0] - margin, size[1] - margin))
        self.shadow = pygame.Rect((pos[0] + margin / 2, pos[1] + margin / 2), (size[0] - margin, size[1] - margin))
        self.width = self.foreground.w

    def update(self, value):
        self.foreground.w = value * (self.width / self.max_value)


class CraftingTable:
    def __init__(self):
        self.opened = False
        self.screen_width, self.screen_height = pygame.display.get_window_size()
        self.inventory = None
        self.hovering = False
        self.holding_item = False
        self.interacted_item = ""
        self.mouse_pos = None
        self.last_index = 0

        self.log_img = pygame.image.load("assets/floor/tile131.png").convert_alpha()
        self.log_img = pygame.transform.scale(self.log_img, (150, 150))

        self.stone_img = pygame.image.load("assets/floor/tile010.png").convert_alpha()
        self.stone_img = pygame.transform.scale(self.stone_img, (150, 150))

        self.tomato_img = pygame.image.load("assets/floor/tile127.png").convert_alpha()
        self.tomato_img = pygame.transform.scale(self.tomato_img, (150, 150))

        self.flower_img = pygame.image.load("assets/floor/tile011.png").convert_alpha()
        self.flower_img = pygame.transform.scale(self.flower_img, (150, 150))

        self.bg_width = 500
        self.bg_height = 500
        self.bg_color = pygame.Color("#212529")
        self.background = pygame.Rect(
            (self.screen_width / 2 - self.bg_width / 2, self.screen_height / 2 - self.bg_height / 2),
            (self.bg_width, self.bg_height)
        )
        self.block_color = pygame.Color("#343a40")
        self.blocks = []
        self.block_fill = {

            0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: ""

        }

        self.recipes = {
            "s  slls  ": "pickaxe ", "   ssl   ": "sword ", "ss sll   ": "axe ", "tff      ": "cookie "
        }
        self.mask_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA, 32)
        self.mask_surf.fill((0, 0, 0, 100))

        for x in range(3):
            for y in range(3):
                self.blocks.append(
                    pygame.Rect(
                        (self.background.x + x * int(self.bg_width / 3) + 8,
                         8 + self.background.y + y * (int(self.bg_height) / 3)),
                        (int(self.bg_width / 3 - 16), int(self.bg_height / 3 - 16))
                    )
                )

    def draw(self, screen):
        if self.opened:
            screen.blit(self.mask_surf, (0, 0))
            pygame.draw.rect(screen, self.bg_color, self.background, border_radius=16)
            for index, block in enumerate(self.blocks):
                if not block.collidepoint(self.mouse_pos[0], self.mouse_pos[1]):
                    pygame.draw.rect(screen, self.block_color, block, border_radius=8)
                else:
                    pygame.draw.rect(screen, (200, 200, 200), block, border_radius=8)
                if self.block_fill[index] == "log ":
                    screen.blit(self.log_img, block)
                elif self.block_fill[index] == "stone ":
                    screen.blit(self.stone_img, block)
                elif self.block_fill[index] == "tomato ":
                    screen.blit(self.tomato_img, block)
                elif self.block_fill[index] == "flower ":
                    screen.blit(self.flower_img, block)

            self.inventory.draw(screen, pygame.mouse.get_pos())
            self.inventory.update(pygame.mouse.get_pressed(), pygame.mouse.get_pos(), screen)

            if self.holding_item:
                if self.interacted_item == "stone ":
                    screen.blit(self.inventory.stone_img, (self.mouse_pos[0] - 15, self.mouse_pos[1] - 15))
                elif self.interacted_item == "log ":
                    screen.blit(self.inventory.log_img, (self.mouse_pos[0] - 15, self.mouse_pos[1] - 15))
                elif self.interacted_item == "tomato ":
                    screen.blit(self.inventory.tomato_img, (self.mouse_pos[0] - 15, self.mouse_pos[1] - 15))
                elif self.interacted_item == "flower ":
                    screen.blit(self.inventory.flower_img, (self.mouse_pos[0] - 15, self.mouse_pos[1] - 15))

    def set_inventory(self, inventory):
        self.inventory = inventory

    def reset(self):
        self.screen_width, self.screen_height = pygame.display.get_window_size()

        self.mask_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA, 32)
        self.mask_surf.fill((0, 0, 0, 100))

        self.background = pygame.Rect(
            (self.screen_width / 2 - self.bg_width / 2, self.screen_height / 2 - self.bg_height / 2),
            (self.bg_width, self.bg_height)
        )

        self.blocks = []

        for x in range(3):
            for y in range(3):
                self.blocks.append(
                    pygame.Rect(
                        (self.background.x + x * int(self.bg_width / 3) + 8,
                         8 + self.background.y + y * (int(self.bg_height) / 3)),
                        (int(self.bg_width / 3 - 16), int(self.bg_height / 3 - 16))
                    )
                )

    def update(self, keys, mouse_pos, mouse_click):
        self.mouse_pos = mouse_pos
        if keys[pygame.K_TAB]:
            if not self.opened:
                self.opened = True
                time.sleep(0.15)
            else:
                self.opened = False
                for key in self.block_fill:
                    if bool(self.block_fill[key]):
                        self.inventory.add_item(self.block_fill[key])
                        self.block_fill[key] = ""

                if self.holding_item:
                    self.inventory.add_item(self.interacted_item)
                    self.holding_item = False
                time.sleep(0.15)

        if self.background.collidepoint(mouse_pos[0], mouse_pos[1]):
            self.hovering = True
        else:
            self.hovering = False

        for index, block in enumerate(self.blocks):
            if block.collidepoint(mouse_pos[0], mouse_pos[1]):
                if mouse_click[0] and self.inventory.holding_item:
                    if self.inventory.clicked_item[0] in ["s", "l", "t", "f"]:
                        self.block_fill[index] = self.inventory.clicked_item
                        self.inventory.holding_item = False

                if mouse_click[1] and not self.holding_item:
                    self.interacted_item = self.block_fill[index]
                    self.block_fill[index] = ""
                    self.holding_item = True

                if mouse_click[0] and self.holding_item and not bool(self.block_fill[index]):
                    self.block_fill[index] = self.interacted_item
                    self.interacted_item = ""
                    self.holding_item = False

                if mouse_click[0] and self.holding_item and bool(self.block_fill[index]):
                    item = self.block_fill[index]
                    self.block_fill[index] = self.interacted_item
                    self.interacted_item = item
                    self.holding_item = True
                    time.sleep(0.1)

        if keys[pygame.K_RETURN]:
            recipe = ""
            for index, block in enumerate(self.blocks):
                if bool(self.block_fill[index]):
                    recipe += self.block_fill[index][0]
                else:
                    recipe += " "

            if recipe in self.recipes:
                self.inventory.add_item(self.recipes[recipe])
                self.block_fill = {

                    0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: "", 9: ""

                }

            time.sleep(0.1)

class Animal:
    def __init__(self, max_spawn, width, height):
        self.max_spawn = max_spawn
        self.animal_list = []
        self.update_frame = time.perf_counter()
        self.animal_frame = 1
        self.update_move = time.perf_counter()
        self.animal_walk_plan = []
        self.screen_width = width
        self.screen_height = height
        self.inventory = None
        self.hit = False

        self.pic_dict = {}
        self.load_images = ["sheep"]
        for load_image in self.load_images:
            for direction in ["front", "right", "back", "left"]:
                for frame in range(1, 5):
                    print(f"assets/sheep/{load_image}{direction}{str(frame)}.png")
                    if not direction == "left":
                        image = pygame.image.load(f"assets/sheep/{load_image}{direction}{str(frame)}.png").convert_alpha()
                    else:
                        image = pygame.image.load(f"assets/sheep/{load_image}right{str(frame)}.png").convert_alpha()
                        image = pygame.transform.flip(image, True, False)
                    self.pic_dict[f"{load_image}{direction}{str(frame)}"] = image

        self.rect = None
        self.animal_dict = {}
        for x in range(self.max_spawn):
            size = random.choice(["small", "big"])
            group = random.randint(0, group_count-1)
            rect = self.pic_dict["sheepright1small"].get_rect(topleft=
                 (group_list[group][0] + random.randint(-250, 250), group_list[group][1] + random.randint(-250, 250)))
            self.spawn_animal(rect, size, group_list[group][2], x)

    def spawn_animal(self, rect, size, animal_type, x):
        if not rect.x < -150 * 16 - 8 and not rect.x > 150 * 16 - 8:
            if not rect.y < -150 * 16 - 8 and not rect.y > 150 * 16 - 8:
                self.animal_dict[x] = [
                    rect,  # ind 0
                    animal_type,  # 1
                    random.choice(["left", "right", "front", "back"]),  # 2
                    1,  # 3
                    random.choice([True, False]),  # 4
                    0,  # 5
                    0,  # 6
                    [],  # 7
                    time.perf_counter(),  # 8
                    random.randint(6, 20),  # 9
                    random.choice(["left", "right", "front", "back"]),
                    1,  # 11
                    time.perf_counter(),  # 12
                    size,
                    random.choice([True, False]),  # 14
                    100  # hp 15
                ]

    def reset_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height

    def draw(self, screen, scrollx, scrolly):
        for animal_key in self.animal_dict:
            animal = self.animal_dict[animal_key]
            animal_rect = animal[0]
            animal_type = animal[1]
            animal_direction = animal[2]
            animal_walking = animal[4]
            animal_draw_direction = animal[10]
            animal_frame = animal[11]
            animal_frame_timer = animal[12]
            animal_size = animal[13]

            if animal_walking and time.perf_counter() - animal_frame_timer > 0.2: #change to next frame
                animal[11] = (animal_frame + 1) % 4
                animal[12] = time.perf_counter()

            if not animal_walking:
                animal[11] = 1

            screen.blit(
                self.pic_dict[
                    f"{animal_type}{animal_draw_direction}{animal[11] + 1}{animal_size}"],
                    (
                        animal_rect.x - scrollx, animal_rect.y - scrolly
                    )
            )

    @staticmethod
    def create_walk_plan(max_steps):
        return_list = []
        waypoint = random.choice(["tl", "tr", "l", "r", "bl", "br", "b", "t"])
        direction = ""
        walk_speed = 0.5
        for x in range(max_steps):
            if waypoint == "tl":
                return_list.append((-walk_speed, -walk_speed))
                direction = "left"
            elif waypoint == "tr":
                return_list.append((walk_speed, -walk_speed))
                direction = "right"
            elif waypoint == "r":
                return_list.append((walk_speed, 0))
                direction = "right"
            elif waypoint == "l":
                return_list.append((-walk_speed, 0))
                direction = "left"
            elif waypoint == "bl":
                return_list.append((-walk_speed, walk_speed))
                direction = "left"
            elif waypoint == "br":
                return_list.append((walk_speed, walk_speed))
                direction = "right"
            elif waypoint == "b":
                return_list.append((0, walk_speed))
                direction = "front"
            elif waypoint == "t":
                return_list.append((0, -walk_speed))
                direction = "back"

        return return_list, direction

    #halofdas

    def update(self, plants, player):
        for animal_key in self.animal_dict:
            animal = self.animal_dict[animal_key]
            animal_rect = animal[0]
            animal_type = animal[1]
            animal_direction = animal[2]
            animal_walking = animal[4]
            animal_path = animal[5]
            animal_set_steps = animal[6]
            animal_walk_plan = animal[7]
            animal_perf = animal[8]
            if time.perf_counter() - animal_perf > random.randint(6, 20):
                if animal_walking:
                    animal[4] = False
                else:
                    animal[4] = True
                    animal[6] = random.randint(5, 20)
                    animal[7] = self.create_walk_plan(animal_set_steps)
                animal[8] = time.perf_counter()
            if animal_walking:
                if animal_path < animal_set_steps:
                    animal_rect.x += animal[7][animal[5]][0]
                    animal_rect.y += animal[7][animal[5]][1]
                    animal[5] += 1
                else:
                    animal[4] = False
                    animal[6] = []
                    animal[5] = 0

            on_tile = (int(animal_rect.x / 16), int(animal_rect.y / 16))

            if not animal_rect.x < -150 * 16 - 32 and not animal_rect.x > 150 * 16 - 32:
                if not animal_rect.y < -150 * 16 - 32 and not animal_rect.y > 150 * 16 - 32:
                    if plants[on_tile[1] + 1, on_tile[0] + 1] in [127, 11] and hungry:
                        plants[on_tile[1] + 1, on_tile[0] + 1] = 0

            if player.x < animal_rect.x + 16 and  player.x > animal_rect.x - 32:
                if player.y < animal_rect.y + 16 and player.y > animal_rect.y - 32:
                    if player.hitting:
                        self.hit = True
                        # maak particles
                        for _ in range(15):
                            particles.append(HitParticle(animal[0].x, animal[0].y))
                        animal[4] = True
                        animal[6] = random.randint(300, 350)
                        animal[7], animal[10] = self.create_walk_plan(animal[6])
                        animal[15] -= random.randint(30, 40)
                        animal_rect.y += random.randint(-5, 5)
                        animal_rect.x += random.randint(-5, 5)
                        player.hitting = False


            if animal_hp <= 0:
                print("killed")


class Inventory:
    def __init__(self, size, pos):
        self.player = None
        self.crafting_table = None
        self.size = size
        self.pos = pos
        self.bar = pygame.Rect(pos, (size[0], size[1] + 2))
        self.block = pygame.Rect((pos[0] + 8, pos[1] - 8), (size[0] - 16, size[1] - 8))
        self.backpack_margin = 55
        self.bar_backback = pygame.Rect((pos[0] + self.backpack_margin, pos[1]), (size[0]*2-2, size[1] + 2))
        self.backpack_block = pygame.Rect((pos[0] + 8 + self.backpack_margin, pos[1] - 8), (size[0] - 16, size[1] - 8))
        self.blocks = [] # 9 normal always visible slots
        self.backpack_blocks = [] # 9 backback slots
        self.block_y = 0
        self.backpack_block_y = 0
        self.colors = ["orange", "grey", "black"]
        self.color = "orange"
        self.block_color = pygame.Color("#343a40")
        self.selected_block = 0
        self.backpack_visible = False
        self.last_time = 0
        self.item_direction = -1
        self.item_speed = 0.3

        self.pic_dict = {}
        self.pic_dict_small = {}
        self.items_dict = {"tomato ": ["assets/floor/tile127.png", 30],
                           "flower " : ["assets/floor/tile011.png", 30],
                           "sword ": ["assets/tools/Sword-1.png", 37],
                           "stone ": ["assets/floor/tile010.png", 30],
                           "axe ": ["assets/tools/axe.png", 33],
                           "log ": ["assets/floor/tile131.png", 33],
                           "meat ": ["assets/food/26.png", 30],
                           "tomato ": ["assets/floor/tile127.png", 30],
                           "flower ": ["assets/floor/tile011.png", 30],
                           "cookie ": ["assets/food/00.png", 30],
                           "pickaxe ": ["assets/tools/pickaxe.png", 33]
                           }

        self.items_dict_small = {"tomato ": ["assets/floor/tile127.png", 15],
                           "flower ": ["assets/floor/tile011.png", 15],
                           "sword ": ["assets/tools/Sword-1.png", 12],
                           "stone ": ["assets/floor/tile010.png", 15],
                           "axe ": ["assets/tools/axe.png", 18],
                           "log ": ["assets/floor/tile131.png", 18],
                           "meat ": ["assets/food/26.png", 15],
                           "tomato ": ["assets/floor/tile127.png", 15],
                           "flower ": ["assets/floor/tile011.png", 15],
                           "cookie ": ["assets/food/00.png", 15],
                           "pickaxe ": ["assets/tools/pickaxe.png", 18]
                           }

        for item in self.items_dict:
            self.pic_dict[item] = pygame.image.load(f"{self.items_dict[item][0]}").convert_alpha()
            self.pic_dict[item] = pygame.transform.scale(self.pic_dict[item], (self.items_dict[item][1], self.items_dict[item][1]))

        for item in self.items_dict_small:
            self.pic_dict_small[item] = pygame.image.load(f"{self.items_dict_small[item][0]}").convert_alpha()
            self.pic_dict_small[item] = pygame.transform.scale(self.pic_dict_small[item], (self.items_dict_small[item][1], self.items_dict_small[item][1]))


        # self.tomato_img = pygame.image.load("assets/floor/tile127.png").convert_alpha()
        # self.flower_img = pygame.image.load("assets/floor/tile011.png").convert_alpha()
        # self.sword_img = pygame.image.load("assets/tools/Sword-1.png").convert_alpha()
        # self.stone_img = pygame.image.load("assets/floor/tile010.png").convert_alpha()
        # self.pickaxe_img = pygame.image.load("assets/tools/pickaxe.png").convert_alpha()
        # self.axe_img = pygame.image.load("assets/tools/axe.png").convert_alpha()
        # self.log_img = pygame.image.load("assets/floor/tile131.png").convert_alpha()
        # self.meat_img = pygame.image.load("assets/food/26.png").convert_alpha()
        # self.meat_img = pygame.transform.scale(self.meat_img, (30, 30))
        # self.cookie_img = pygame.image.load("assets/food/00.png").convert_alpha()
        # self.tomato_img = pygame.transform.scale(self.tomato_img, (30, 30))
        # self.flower_img = pygame.transform.scale(self.flower_img, (30, 30))
        # self.stone_img = pygame.transform.scale(self.stone_img, (30, 30))
        # self.sword_img = pygame.transform.scale(self.sword_img, (37, 37))
        # self.pickaxe_img = pygame.transform.scale(self.pickaxe_img, (33, 33))
        # self.axe_img = pygame.transform.scale(self.axe_img, (33, 33))
        # self.log_img = pygame.transform.scale(self.log_img, (33, 33))
        # self.cookie_img = pygame.transform.scale(self.cookie_img, (30, 30))

        self.description = ""
        self.font = pygame.font.Font("assets/Font/SpaceMono-Regular.ttf", 12)
        self.clicked_item = ""
        self.holding_item = False
        self.can_fill = True
        self.eating_sound = pygame.mixer.Sound("assets/sounds/eating.wav")
        self.hovering_menu = False
        self.holding_pickaxe = False
        self.holding_axe = False
        self.dropped_items = []
        self.given_items = {0: "axe ", 1: "pickaxe ", 2: "tomato ", 3: "sword "}
        self.block_fill = {}
        self.dropped_items = {}
        for i in range(27):
            self.block_fill[i] = self.given_items[i] if i in self.given_items else ""


        self.full_key_dict = {

            0: True, 1: True, 2: True, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False,
            9: False, 10: False, 11: False, 12: False, 13: False, 14: False, 15: False, 16: False, 17: False,
            18: False, 19: False, 20: False, 21: False, 22: False, 23: False, 24: False, 25: False, 26: False

        }

        for x in range(9):
            self.blocks.append(pygame.Rect(pos[0] + 8, pos[1] + self.block_y + 8, size[0] - 16, size[1] / 10.5 - 8))
            self.block_y += size[1] / 9

    def add_item(self, item):
        if not bool(self.block_fill[self.selected_block]):
            self.block_fill[self.selected_block] = item
        else:
            for x in range(27):
                if not bool(self.block_fill[x]):
                    self.block_fill[x] = item
                    break

    def get_player(self, player):
        self.player = player

    def set_crafting_table(self, crafting_table):
        self.crafting_table = crafting_table

    def reset_pos(self, pos):
        self.bar = pygame.Rect(pos, (self.size[0], self.size[1] + 2))

        self.block_y = 0
        self.blocks = []

        for x in range(9):
            self.blocks.append(
                pygame.Rect(pos[0] + 8, pos[1] + self.block_y + 8, self.size[0] - 16, self.size[1] / 10.5 - 8))
            self.block_y += self.size[1] / 9

        self.backpack_margin = 55
        self.bar_backback = pygame.Rect((pos[0] + self.backpack_margin, pos[1]), (self.size[0]*2-2, self.size[1] + 2))
        self.backpack_block = pygame.Rect((pos[0] + 8 + self.backpack_margin, pos[1] - 8), (self.size[0] - 16, self.size[1] - 8))
        self.backpack_block_y = 0

        self.block_y = 0

        for x in range(9):
            self.blocks.append(
                pygame.Rect(pos[0] + 8 + self.backpack_margin, pos[1] + self.block_y + 8, self.size[0] - 16, self.size[1] / 10.5 - 8))
            self.block_y += self.size[1] / 9

        self.backpack_block_y = 0

        for x in range(9):
            self.blocks.append(
                pygame.Rect(pos[0] + self.backpack_margin * 2, pos[1] + self.backpack_block_y + 8,
                            self.size[0] - 16, self.size[1] / 10.5 - 8))
            self.backpack_block_y += self.size[1] / 9

    def draw(self, screen, pos, scrollx, scrolly):
        pygame.draw.rect(screen, pygame.Color("#212529"), self.bar, border_radius=8)
        if self.backpack_visible:
            pygame.draw.rect(screen, pygame.Color("#212529"), self.bar_backback, border_radius=8)

        # for index, block in enumerate(self.blocks):
        #
        #     pygame.draw.rect(screen, self.block_color, block, border_radius=4)
        #
        #     if block.collidepoint(pos[0], pos[1]) and (self.holding_item or self.crafting_table.holding_item):
        #         pygame.draw.rect(screen, (150, 150, 150), block, border_radius=4)
        #
        #
        #     if self.block_fill[index] != '':
        #         screen.blit(self.pic_dict[self.block_fill[index]], block)

        for i in self.dropped_items:
            item = self.dropped_items[i]
            image_code = item[0]
            screen.blit(
                self.pic_dict_small[image_code],
                (item[1] - scrollx, item[2] - scrolly)
            )
            if time.perf_counter() - self.last_time > 0.5:
                self.last_time = time.perf_counter()
                if self.item_direction == 1:
                    self.item_direction = -1
                else:
                    self.item_direction = 1

            print(get_distance(item[1], item[2], self.player.x + 24, self.player.y + 24))

            item[2] += self.item_direction * self.item_speed

            if get_distance(item[1], item[2], self.player.x + 12, self.player.y + 12) < 50:
                item[1] -= (item[1] - self.player.x - 12) / 5
                item[2] -= (item[2] - self.player.y) / 5
                if get_distance(item[1], item[2], self.player.x + 12, self.player.y + 12) < 17:
                    self.add_item(item[0])
                    self.dropped_items.pop(i)
                    break

            if time.perf_counter() - item[3] > 60*5: # 5 minutes
                self.dropped_items.pop(i)
                break

        for index, block in enumerate(self.blocks):

            if not index > 8:
                if index == self.selected_block:
                    pygame.draw.rect(screen, (200, 200, 200), block, border_radius=4)
                else:
                    pygame.draw.rect(screen, self.block_color, block, border_radius=4)

                if block.collidepoint(pos[0], pos[1]) and (self.holding_item or self.crafting_table.holding_item):
                    pygame.draw.rect(screen, (150, 150, 150), block, border_radius=4)
            elif self.backpack_visible:
                if index == self.selected_block:
                    pygame.draw.rect(screen, (200, 200, 200), block, border_radius=4)
                else:
                    pygame.draw.rect(screen, self.block_color, block, border_radius=4)

                if block.collidepoint(pos[0], pos[1]) and (self.holding_item or self.crafting_table.holding_item):
                    pygame.draw.rect(screen, (150, 150, 150), block, border_radius=4)

            # if self.block_fill[index] == "tomato ":
            #     screen.blit(self.tomato_img, block)
            #
            # if self.block_fill[index] == "flower ":
            #     screen.blit(self.flower_img, block)
            #
            # if self.block_fill[index] == "sword ":
            #     screen.blit(self.sword_img, block)
            #
            # if self.block_fill[index] == "stone ":
            #     screen.blit(self.stone_img, block)
            #
            # if self.block_fill[index] == "pickaxe ":
            #     screen.blit(self.pickaxe_img, block)
            #
            # if self.block_fill[index] == "axe ":
            #     screen.blit(self.axe_img, block)
            #
            # if self.block_fill[index] == "log ":
            #     screen.blit(self.log_img, block)
            #
            # if self.block_fill[index] == "cookie ":
            #     screen.blit(self.cookie_img, block)
            #
            # if self.block_fill[index] == "meat ":
            #     screen.blit(self.meat_img, block)

            if not index > 8:
                if self.block_fill[index] != '':
                    screen.blit(self.pic_dict[self.block_fill[index]], block)
            elif self.backpack_visible:
                if self.block_fill[index] != '':
                    screen.blit(self.pic_dict[self.block_fill[index]], block)

            self.color = random.choice(self.colors)

    def update(self, keys, pos, screen, keyboard):
        holding_item = False
        clicked_item = ""

        if self.bar.collidepoint(pos[0], pos[1]) or self.bar_backback.collidepoint(pos):
            self.hovering_menu = True
        else:
            self.hovering_menu = False

        for key in self.block_fill:
            if bool(self.block_fill[key]):
                self.full_key_dict[key] = True
            else:
                self.full_key_dict[key] = False

        if all(value == True for value in self.full_key_dict.values()):
            self.can_fill = False
        else:
            self.can_fill = True

        for index, block in enumerate(self.blocks):
            current_block = pygame.Rect((-500, 0), (0, 0))

            if self.block_fill[self.selected_block] == "tomato ":
                if keys[2] and not self.player.on_interact:
                    if keys[2] and self.player.food_value < 10000 - self.player.tomato_feeding:
                        self.player.food_value += self.player.tomato_feeding
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.food_value < 10000:
                        self.player.food_value = 10000
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "cookie ":
                if keys[2] and not self.player.on_interact:
                    if keys[2] and self.player.food_value < 10000 - self.player.cookie_feeding:
                        self.player.food_value += self.player.cookie_feeding
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.food_value < 10000:
                        self.player.food_value = 10000
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "meat ":
                if keys[2] and not self.player.on_interact:
                    if keys[2] and self.player.food_value < 10000 - self.player.cookie_feeding:
                        self.player.food_value += self.player.cookie_feeding
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.food_value < 10000:
                        self.player.food_value = 10000
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "flower ":
                if keys[2] and not self.player.on_interact:
                    if keys[2] and self.player.energy_value < 100 - self.player.flower_power:
                        self.player.energy_value += self.player.flower_power
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)
                    elif keys[2] and self.player.energy_value < 100:
                        self.player.energy_value = 100
                        self.block_fill[self.selected_block] = ""
                        pygame.mixer.Sound.play(self.eating_sound)

            if self.block_fill[self.selected_block] == "sword ":
                self.player.sword_selected = True
            else:
                self.player.sword_selected = False

            if self.block_fill[self.selected_block] == "pickaxe ":
                self.holding_pickaxe = True
            else:
                self.holding_pickaxe = False

            if self.block_fill[self.selected_block] == "axe ":
                self.holding_axe = True
            else:
                self.holding_axe = False

            if block.collidepoint(pos[0], pos[1]):
                if not index > 8 or self.backpack_visible:
                    current_block = block
                    current_index = index
                    if not index > 8:
                        if keys[0]:
                            self.selected_block = current_index
                    if self.block_fill[index] == "tomato ":
                        self.description = "Tomato's will make you less hungry  |  [RMB] to consume"
                    elif self.block_fill[index] == "flower ":
                        self.description = "Flowers refill your energy  |  [RMB] to consume"
                    elif self.block_fill[index] == "sword ":
                        self.description = "With the sword you can attack living things  |  [LMB] to attack"
                    elif self.block_fill[index] == "pickaxe ":
                        self.description = "With a pickaxe you can mine stone  |  [E] to mine"
                    elif self.block_fill[index] == "stone ":
                        self.description = "You can use stone to craft items  |  [TAB] to open crafting table"
                    elif self.block_fill[index] == "axe ":
                        self.description = "With an axe you can cut down trees  |  [E] to cut"
                    elif self.block_fill[index] == "log ":
                        self.description = "With logs you can craft items |  [TAB] to open crafting table"
                    elif self.block_fill[index] == "cookie ":
                        self.description = "Cookies are a great source of food  |  [RMB] to consume"
                    elif self.block_fill[index] == "meat ":
                        self.description = "Meat is a very nutritious type of food  |  [RMB] to consume"
                    else:
                        self.description = ""

            if not index > 8 or self.backpack_visible:
                if self.holding_item:
                    screen.blit(self.pic_dict[self.clicked_item], (pos[0], pos[1]))

                if keys[1] and block.collidepoint(pos[0], pos[1]) and bool(
                        self.block_fill[index]) and not self.holding_item:
                    clicked_block = index
                    clicked_item = self.block_fill[clicked_block]
                    self.clicked_item = clicked_item
                    self.block_fill[clicked_block] = ""
                    self.holding_item = True

                # if keys[0] and block.collidepoint(pos[0], pos[1]) and not bool(
                #         self.block_fill[index]) and self.holding_item:
                if keys[0] and block.collidepoint(pos[0], pos[1]) and self.block_fill[index] in ["", " "] and self.holding_item:
                    self.block_fill[index] = self.clicked_item
                    self.holding_item = False
                #elif keys[0] and block.collidepoint(pos[0], pos[1]):
                #    print(f"/{self.block_fill[index]}/", self.holding_item)

                if keys[0] and block.collidepoint(pos[0], pos[1]) and bool(self.block_fill[index]) and self.holding_item:
                    item = self.block_fill[index]
                    self.block_fill[index] = self.clicked_item
                    self.clicked_item = item
                    self.holding_item = True
                    time.sleep(0.1)

                if keys[0] and block.collidepoint(pos[0], pos[1]) and not bool(
                        self.block_fill[index]) and self.crafting_table.holding_item:
                    self.block_fill[index] = self.crafting_table.interacted_item
                    self.crafting_table.holding_item = False

                if self.holding_item and keys[0] and not self.hovering_menu and not self.crafting_table.opened:
                    if not self.clicked_item == "":
                        self.dropped_items[
                            len(self.dropped_items)] = [
                            self.clicked_item,
                            self.player.x + random.choice([-60, 60, 55, -55]), self.player.y + random.choice([-60, 60, 55, -55]),
                            time.perf_counter()
                        ]
                        self.clicked_item = ""
                        self.holding_item = False

                if keyboard[pygame.K_q] and not self.block_fill[self.selected_block] == "":
                    self.dropped_items[
                        len(self.dropped_items)] = [
                        self.block_fill[self.selected_block],
                        self.player.x + random.choice([-60, 60, 55, -55]), self.player.y + random.choice([-60, 60, 55, -55]),
                        time.perf_counter()
                    ]
                    self.block_fill[self.selected_block] = ""

            if bool(self.description):
                text_w, text_h = self.font.size(self.description)
                text_render = self.font.render(self.description, True, "white")
                bg_rect = pygame.Rect((current_block.x + 50, current_block.y), (text_w + 15, text_h + 15))
                shadow_rect = pygame.Rect((current_block.x + 52, current_block.y + 2), (text_w + 15, text_h + 15))
                pygame.draw.rect(screen, pygame.Color("#30363b"), shadow_rect, border_radius=8)
                pygame.draw.rect(screen, pygame.Color("#212529"), bg_rect, border_radius=8)
                screen.blit(text_render, (current_block.x + 50 + 7, current_block.y + 7))

    def mouse_update(self, mouse):
        if mouse > 0:
            if self.selected_block == 0:
                self.selected_block = 8
            else:
                self.selected_block -= 1
        elif mouse < 0:
            if self.selected_block == 8:
                self.selected_block = 0
            else:
                self.selected_block += 1


def load_img():
    images = {}

    for x in range(130):
        if x > 99:
            tile_num = str(x)
        elif x > 9:
            tile_num = f"0{x}"
        else:
            tile_num = f"00{x}"

        images[f"tile{x}"] = pygame.image.load(f"assets/floor/tile{tile_num}.png")

    for x in os.listdir("assets/character"):
        images[f"{x[:-4]}"] = pygame.image.load((f"assets/character/{x}"))
        images[f"{x[:-4]}_flipped"] = pygame.transform.flip(pygame.image.load((f"assets/character/{x}")), True, False)

    return images


def create_world(map_w, map_h, chance_index):
    map_w, map_h = map_w + 4, map_h + 4 #add four to width and height to cut it out later, easier world generation with no edges

    from perlin_noise import PerlinNoise

    noise = PerlinNoise(seed=random.randint(1, 1000000), octaves=10)

    world_gen = numpy.zeros((map_w, map_h))
    for x in range(map_w):
        for y in range(map_h):
            world_gen[y, x] = noise([x / map_w, y / map_h])

    world = numpy.zeros((map_h, map_w), dtype=int)
    plants = numpy.zeros((map_h, map_w), dtype=int)
    world_rotation = numpy.zeros((map_h, map_w), dtype=int)

    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_gen[y, x] > 0:
                world[y, x] = random.choice([5, 6, 7])
                # plants[y, x] = 12
            else:
                world[y, x] = 14
                if random.randint(0, chance_index) == 1:
                    plants[y, x] = random.choice([123, 124, 125, 126, 11, 8, 10, 110, 111, 112, 113, 127])
                else:
                    pass
                    # plants[y, x] = 12

    world_copy = world
    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_copy[y, x] in [5, 6, 7]:
                if not (x == 0 or y == 0 or x == world.shape[1] - 1 or y == world.shape[1] - 1):  # rand van wereld
                    grass_code = ""
                    grass_count = 0
                    for c in [world_copy[y - 1, x], world_copy[y, x + 1], world_copy[y + 1, x], world_copy[y, x - 1]]:
                        if c == 14:
                            grass_count += 1
                            grass_code += "g"
                        else:
                            grass_code += "s"
                    if grass_count > 2:
                        world[y, x] = 14
                    if grass_code in ["gsgs", "sgsg"]:
                        world[y, x] = 14

    world_copy = world
    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_copy[y, x] in [5, 6, 7]:
                convert = False
                if x == 0 or y == 0 or x == world.shape[1] - 1 or y == world.shape[1] - 1:  # rand van wereld
                    convert = True
                    check_code = "ssss"  # tijdelijk

                    # boven                  # rechts                  # onder              # links
                elif world_copy[y - 1, x] == 14 or world_copy[y, x + 1] == 14 or world_copy[y + 1, x] == 14 or \
                        world_copy[y, x - 1] == 14:
                    convert = True
                    # check code: pos 0 = boven pos 1 = rechts pos 2 = onder, pos 3 = links
                    check_code = ""

                    for c in [world_copy[y - 1, x], world_copy[y, x + 1], world_copy[y + 1, x], world_copy[y, x - 1]]:
                        if c == 14:
                            check_code += "g"  # grass
                        else:  # 4,5,6
                            check_code += "s"  # sand
                if convert:  # volgorde: boven, rechts, onder, links
                    convert_dict = {"sssg": 15, "ssgs": 21, "sgss": 23, "gsss": 35, "gssg": 16, "ggss": 17, "ssgg": 20,
                                    "sggs": 19}
                    if check_code in convert_dict:
                        world[y, x] = convert_dict[check_code]

    world_copy_copy = world
    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_copy_copy[y, x] in [5, 6, 7]:
                if not (x == 0 or y == 0 or x == world.shape[1] - 1 or y == world.shape[1] - 1):  # rand van wereld
                    generated_tiles = 0
                    gen_code = ""
                    for c in [world_copy_copy[y - 1, x], world_copy_copy[y, x + 1], world_copy_copy[y + 1, x],
                              world_copy_copy[y, x - 1]]:
                        if c in [15, 21, 23, 35, 16, 17, 20, 19]:
                            generated_tiles += 1
                        if c in [5, 6, 7]:
                            gen_code += f"5-"
                        else:
                            gen_code += f"{c}-"

                    if generated_tiles == 2:  # boven, rechts, onder, links
                        gen_code = gen_code[:-1]
                        convert_dict = {"17-35-5-5": 26, "17-17-5-5": 26, "23-17-5-5": 26, "23-35-5-5": 26,

                                        "15-5-5-35": 28, "15-5-5-16": 28, "16-5-5-35": 28, "16-5-5-16": 28,

                                        "5-21-19-5": 25, "5-19-23-5": 25, "5-19-19-5": 25, "5-21-23-5": 25,

                                        "5-5-15-20": 34, "5-5-20-21": 34, "5-5-15-21": 34, "5-5-20-20": 34
                                        }

                        if gen_code in convert_dict:
                            world[y, x] = convert_dict[gen_code]

    with open("convert_tiles.json") as f:
        convert_dict = json.load(f)

    world_copy_copy = world
    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_copy_copy[y, x] in [5, 6, 7]:
                if not (x == 0 or y == 0 or x == world.shape[1] - 1 or y == world.shape[1] - 1):  # rand van wereld
                    generated_tiles = 0
                    gen_code = ""
                    for c in [world_copy_copy[y - 1, x], world_copy_copy[y, x + 1], world_copy_copy[y + 1, x],
                              world_copy_copy[y, x - 1]]:
                        if c in [15, 21, 23, 35, 16, 17, 20, 19, 26, 28, 25, 34]:
                            generated_tiles += 1
                        if c in [5, 6, 7]:
                            gen_code += f"5-"
                        else:
                            gen_code += f"{c}-"

                    if generated_tiles > 2:  # boven, rechts, onder, links
                        gen_code = gen_code[:-1]

                        if gen_code in convert_dict:
                            world[y, x] = convert_dict[gen_code]
                            # if convert_dict[gen_code] == -1: #temp
                            #     world[y, x] = 18
                            #
                        # else:
                        #     world[y, x] = 12


    tree_spawn_attempts = 1000

    for _ in range(tree_spawn_attempts):  # grass = 14
        x = random.randint(2, map_w - 6)
        y = random.randint(2, map_h - 6)

        spawn_tree = True
        for sec_x in [x - 1, x, x + 1, x + 2]:
            for sec_y in [y - 1, y, y + 1, y + 2]:
                if world[sec_y, sec_x] not in [14] or plants[sec_y, sec_x] in [48, 49, 61, 62]:
                    spawn_tree = False

        if spawn_tree:
            plants[y, x] = 48
            plants[y, x + 1] = 49
            plants[y + 1, x] = 61
            plants[y + 1, x + 1] = 62

    world = world[2:map_w-2, 2:map_h-2]
    plants = plants[2:map_w-2, 2:map_h-2]
    return plants, world, world_rotation


def render_world(screen, world, plants, world_rotation, images, scrollx, scrolly, screenW, screenH):
    world_h, world_w = world.shape
    tile_size = 16

    draw_x_from = int(scrollx / tile_size)
    draw_x_to = int((scrollx + screenW) / tile_size) + 1

    draw_y_from = int(scrolly / tile_size)
    draw_y_to = int((scrolly + screenH) / tile_size) + 1

    for x in range(draw_x_from, min(draw_x_to, world_w)):
        for y in range(draw_y_from, min(draw_y_to, world_h)):
            screen.blit(images[f"tile{world[y, x]}"], (x * tile_size - scrollx, y * tile_size - scrolly))
            if plants[y, x] != 0:
                screen.blit(images[f"tile{plants[y, x]}"], (x * tile_size - scrollx, y * tile_size - scrolly))


def spawn_particles(particle_perf, player, particles):
    particle_y_offset = 34
    if player.direction_xy == "UP":
        particle_y_offset = 24
    if player.state == "run":
        if time.perf_counter() - particle_perf >= 0.001:
            particles.append(WalkParticle(player.x + 24, player.y + particle_y_offset))
            particle_perf = time.perf_counter()
    elif player.state == "walk":
        if time.perf_counter() - particle_perf >= 0.12:
            particles.append(WalkParticle(player.x + 24, player.y + particle_y_offset))
            particle_perf = time.perf_counter()
    return particles, particle_perf
