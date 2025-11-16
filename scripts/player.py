import pygame
from func import *
from scripts.particle import *
from scripts.placeItem import *
import random
import math


class Player:
    def __init__(self, images, x, y, controller_type):
        self.x = x
        self.y = y

        self.images = images
        self.speed = 0.10
        self.speed_multiplier = 1
        self.food_multiplier = 1
        self.backpack_unlocked = False
        self.increment_boost = 0
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
        self.max_health = 10
        self.strength = 1
        self.tomato_feeding = 1000
        self.cookie_feeding = 2500
        self.flower_power = 40
        self.player_tile = (0, 0)
        if controller_type == "":
            self.interact_img = pygame.image.load(
                "assets/icons/Interact.png"
            ).convert_alpha()
        elif controller_type == "Xbox 360 Controller":
            self.interact_img = pygame.image.load(
                "assets/icons/Interact-Y.png"
            ).convert_alpha()
        elif controller_type == "PS4 Controller":
            self.interact_img = pygame.image.load(
                "assets/icons/Interact-PS4.png"
            ).convert_alpha()

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

        self.pickaxe_img_1 = pygame.image.load(
            "assets/tools/pickaxe.png"
        ).convert_alpha()
        self.pickaxe_img_2 = pygame.transform.rotate(self.pickaxe_img_1, -45)

        self.pickaxe_img_2_flipped = pygame.transform.flip(
            self.pickaxe_img_2, True, False
        )
        self.pickaxe_img_1_flipped = pygame.transform.flip(
            self.pickaxe_img_1, True, False
        )
        self.pickaxe_frame = 0
        self.pickaxe_list = [self.pickaxe_img_1, self.pickaxe_img_2]
        self.pickaxe_list_flip = [
            self.pickaxe_img_1_flipped,
            self.pickaxe_img_2_flipped,
        ]
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
        self.sword_list_flipped = [
            self.sword_img_1_flip,
            self.sword_img_2_flip,
            self.sword_img_3_flip,
        ]
        self.sword_frame = 0
        self.framed = 0
        self.attacking = False
        self.can_attack = True
        self.sword_selected = False
        self.bow_selected = False
        self.hitting = False
        self.attack_delay = 0.8
        self.update_frame_1 = 0
        self.cooldown = 0
        self.stone_rect = pygame.Rect((self.screen_size[0] / 2 - 100, 100), (200, 30))
        self.stone_rect2 = pygame.Rect((self.screen_size[0] / 2 - 100, 100), (200, 30))
        self.stone_rect3 = pygame.Rect(
            (self.screen_size[0] / 2 - 108, 100 - 8), (216, 46)
        )

        self.sword_sweep_sound = pygame.mixer.Sound("assets/sounds/sword_swoosh.wav")
        self.damage_sound = pygame.mixer.Sound("assets/sounds/damage.wav")
        self.damaging = False

        self.poisoned = False
        self.poison_time = -1  # perf counter when poison is gone
        self.poison_duration = 7

        self.hp_bar_color = pygame.Color("#ae2012")

        self.green_hp_icon = pygame.image.load(
            "assets/icons/health_icon_green.png"
        ).convert_alpha()
        self.red_hp_icon = pygame.image.load(
            "assets/icons/health_icon_red.png"
        ).convert_alpha()
        self.hp_icon = self.red_hp_icon
        self.holding_lantern = False

    def set_window_size(self, screen):
        self.screen_size = screen.get_size()

    def walking(
        self,
        keys,
        deltaT,
        mouse,
        joystick,
        joystick_input,
        joystick_btn_dict,
        plants,
        dt,
    ):
        self.state = "idle"
        if joystick_input:
            axis_x, axis_y = (joystick.get_axis(0), joystick.get_axis(1))
            if abs(axis_x) > 0.1:
                self.x += axis_x * 10 * self.speed * dt * self.speed_multiplier
            if abs(axis_y) > 0.1:
                self.y += axis_y * 10 * self.speed * dt * self.speed_multiplier

            self.collision_tile = (int((self.x + 24) / 16), int((self.y + 24) / 16))
            if plants[self.collision_tile[1], self.collision_tile[0]] == 139:
                if abs(axis_x) > 0.1:
                    self.x -= axis_x * 10 * self.speed * dt * self.speed_multiplier
                if abs(axis_y) > 0.1:
                    self.y -= axis_y * 10 * self.speed * dt * self.speed_multiplier

            # button X on controller pressed
            if eval(joystick_btn_dict["south-btn"]) and self.energy_value > 0:
                if self.energy_value > 0.025 * deltaT:
                    self.speed = 0.525
                    self.state = "run"
                self.energy_value -= 0.025 * deltaT
            else:
                self.speed = 0.1
                self.state = "walk"
                if self.energy_value < 100 and not eval(joystick_btn_dict["south-btn"]):
                    self.energy_value += 0.01 * deltaT

            if self.state != "idle":
                if axis_x > 0.15:
                    self.direction = "RIGHT"
                    self.direction_xy = "RIGHT"
                elif axis_x < -0.15:
                    self.direction = "LEFT"
                    self.direction_xy = "LEFT"

            if abs(axis_x) < 0.1 and abs(axis_y) < 0.1:
                self.state = "idle"
                if self.energy_value < 100:
                    self.energy_value += 0.02 * deltaT

            if (
                self.can_attack
                and self.sword_selected
                and not self.attacking
                and not self.inventory.holding_item
                and not self.inventory.hovering_menu
            ):
                if eval(joystick_btn_dict["east-btn"]) and self.energy_value > 15:
                    self.attacking = True
                    self.hitting = True
                    self.framed = 0
                    self.sword_frame = 0
                    self.energy_value -= 15
                    self.food_value -= 10
                    pygame.mixer.Sound.play(self.sword_sweep_sound)

            if self.attacking and self.framed < 3:
                if time.perf_counter() - self.sword_update > 0.0855:
                    self.sword_update = time.perf_counter()
                    self.sword_frame = (self.sword_frame + 1) % 3
                    self.framed += 1
            else:
                self.attacking = False
                self.hitting = False

        else:
            if (
                keys[pygame.K_LSHIFT]
                and self.energy_value > 0
                and (
                    keys[pygame.K_d]
                    or keys[pygame.K_a]
                    or keys[pygame.K_s]
                    or keys[pygame.K_w]
                )
            ):
                if self.energy_value > 0.025 * deltaT:
                    self.speed = 0.525
                    self.state = "run"
                self.energy_value -= 0.025 * deltaT
            elif (
                keys[pygame.K_d]
                or keys[pygame.K_a]
                or keys[pygame.K_s]
                or keys[pygame.K_w]
            ):
                self.speed = 0.1
                self.state = "walk"
                if self.energy_value < 100:
                    self.energy_value += 0.01 * deltaT
            else:
                if self.energy_value < 100:
                    self.energy_value += 0.02 * deltaT

            if (
                self.can_attack
                and self.sword_selected
                and not self.attacking
                and not self.inventory.holding_item
                and not self.inventory.hovering_menu
            ):
                if mouse[0] and self.energy_value > 15:
                    self.attacking = True
                    self.hitting = True
                    self.framed = 0
                    self.sword_frame = 0
                    self.energy_value -= 15
                    self.food_value -= 10
                    pygame.mixer.Sound.play(self.sword_sweep_sound)

            if self.attacking and self.framed < 3:
                if time.perf_counter() - self.sword_update > 0.0855:
                    self.sword_update = time.perf_counter()
                    self.sword_frame = (self.sword_frame + 1) % 3
                    self.framed += 1
            else:
                self.attacking = False
                self.hitting = False

            prev_x, prev_y = self.x, self.y
            if keys[pygame.K_d] and keys[pygame.K_w]:
                self.x += (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.y -= (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.direction = "RIGHT"
                self.direction_xy = "RIGHT"

            elif keys[pygame.K_d] and keys[pygame.K_s]:
                self.x += (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.y += (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.direction = "RIGHT"
                self.direction_xy = "RIGHT"

            elif keys[pygame.K_w] and keys[pygame.K_a]:
                self.x -= (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.y -= (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.direction = "LEFT"
                self.direction_xy = "LEFT"

            elif keys[pygame.K_s] and keys[pygame.K_a]:
                self.x -= (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.y += (
                    100 * self.speed / numpy.sqrt(200) * dt * self.speed_multiplier
                )
                self.direction = "LEFT"
                self.direction_xy = "LEFT"

            else:
                if keys[pygame.K_d]:
                    self.x += 10 * self.speed * dt * self.speed_multiplier
                    if self.state != "run":
                        self.state = "walk"
                    self.direction = "RIGHT"
                    self.direction_xy = "RIGHT"

                if keys[pygame.K_a]:
                    self.x -= 10 * self.speed * dt * self.speed_multiplier
                    if self.state != "run":
                        self.state = "walk"
                    self.direction = "LEFT"
                    self.direction_xy = "LEFT"

                if keys[pygame.K_s]:
                    self.y += 10 * self.speed * dt * self.speed_multiplier
                    if self.state != "run":
                        self.state = "walk"
                    self.direction_xy = "DOWN"

                if keys[pygame.K_w]:
                    self.y -= 10 * self.speed * dt * self.speed_multiplier
                    if self.state != "run":
                        self.state = "walk"
                    self.direction_xy = "UP"

            self.collision_tile = (
                min(
                    max(int((self.x + 24) / 16), 0),
                    149,
                ),
                min(
                    max(int((self.y + 24) / 16), 0),
                    149,
                ),
            )
            if plants[self.collision_tile[1], self.collision_tile[0]] == 139:
                self.x = prev_x
                self.y = prev_y

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
                self.food_value -= 0.01 * deltaT * self.food_multiplier
            elif self.state == "walk":
                self.food_value -= 0.010 * deltaT * self.food_multiplier
            elif self.state == "run":
                self.food_value -= 0.02 * deltaT * self.food_multiplier

    def draw(self, screen, scrollx, scrolly, player_bow):
        scr_w, scr_h = screen.get_size()

        if self.sword_selected:
            if self.direction == "RIGHT" or self.direction_xy == "RIGHT":
                screen.blit(
                    self.sword_list[self.sword_frame],
                    (self.x - 1 - scrollx + 35, self.y - 1 - scrolly + 5),
                )
            if self.direction == "LEFT" or self.direction_xy == "LEFT":
                screen.blit(
                    self.sword_list_flipped[self.sword_frame],
                    (self.x - 1 - scrollx + 12 - 30, self.y - 1 - scrolly + 5),
                )

        if self.inventory.holding_pickaxe:
            if self.direction == "RIGHT" or self.direction_xy == "RIGHT":
                screen.blit(
                    self.pickaxe_list[self.pickaxe_frame],
                    (self.x - 1 - scrollx + 35, self.y - 1 - scrolly + 5),
                )
            if self.direction == "LEFT" or self.direction_xy == "LEFT":
                screen.blit(
                    self.pickaxe_list_flip[self.pickaxe_frame],
                    (self.x - 1 - scrollx + 20 - 30, self.y - 1 - scrolly + 5),
                )

        if self.inventory.holding_axe:
            if self.direction == "RIGHT" or self.direction_xy == "RIGHT":
                screen.blit(
                    self.axe_list_flip[self.axe_frame],
                    (self.x - 1 - scrollx + 35, self.y - 1 - scrolly + 5),
                )
            if self.direction == "LEFT" or self.direction_xy == "LEFT":
                screen.blit(
                    self.axe_list[self.axe_frame],
                    (self.x - 1 - scrollx + 20 - 30, self.y - 1 - scrolly + 5),
                )

        if self.direction == "RIGHT":
            screen.blit(
                self.images[eval(f"self.{self.state}_frames[self.{self.state}_frame]")],
                (int(self.x) - scrollx, int(self.y) - scrolly),
            )
        elif self.direction == "LEFT":
            screen.blit(
                self.images[
                    eval(f"self.{self.state}_frames[self.{self.state}_frame]")
                    + "_flipped"
                ],
                (int(self.x) - scrollx, int(self.y) - scrolly),
            )

        if self.on_interact:
            screen.blit(
                self.interact_img,
                (self.x - 1 - scrollx + 12, self.y - 1 - scrolly - 20),
            )
            # pygame.draw.rect(screen, pygame.Color("#212529"), self.interact_rect, border_radius=15)
            screen.blit(self.interact_render, ((scr_w - self.inter_w) / 2, 15))

        if self.bow_selected:
            player_bow.draw(screen, scrollx, scrolly)

    def get_inventory(self, inventory):
        self.inventory = inventory

    def update(
        self,
        plants,
        keys,
        screen,
        joystick,
        joystick_input,
        health_bar,
        joystick_btn_dict,
        player_bow,
        mouse_pos,
        scrollx,
        scrolly,
        dt,
        particles,
    ):
        self.player_tile = (int(self.x / 16), int(self.y / 16))

        mouse_x, mouse_y = mouse_pos
        mouse_x += scrollx
        mouse_y += scrolly
        dx_mouse = mouse_x - self.x
        dy_mouse = mouse_y - self.y
        dx_mouse = 0.01 if dx_mouse == 0 else dx_mouse
        dy_mouse = 0.01 if dy_mouse == 0 else dy_mouse
        tan_angle = dy_mouse / dx_mouse
        angle = math.degrees(math.atan(tan_angle))

        if abs(dx_mouse) != dx_mouse:
            angle += 180

        if self.bow_selected:
            player_bow.update(self.x + 48 / 2, self.y + 48 / 2, int(angle), dt)

        if self.damaging:
            pygame.mixer.Sound.play(self.damage_sound)
            self.damaging = False

        if plants[self.player_tile[1] + 1, self.player_tile[0] + 1] in [
            127,
            11,
            132,
            133,
            134,
            135,
            136,
            137,
            61,
            138,
            139,
        ]:
            self.on_interact = True
            plant = plants[self.player_tile[1] + 1, self.player_tile[0] + 1]
            if plant == 127:
                self.interact_message = "Harvest tomato"
            elif plant == 11:
                self.interact_message = "Harvest flower"
            elif plant == 61:
                self.interact_message = "Cut down tree (only with axe)"
            elif plant in [132, 133, 134, 135, 136, 137]:
                self.interact_message = "Mine stone (only with pickaxe)"
            elif plant == 138:
                self.interact_message = "Pick up torch"
            elif plant == 139:
                self.interact_message = "Pick up wood"

            text_w, text_h = self.font.size(self.interact_message)
            self.interact_render = pygame.Surface(
                (text_w + 15, text_h + 15), pygame.SRCALPHA
            )
            self.inter_w, self.inter_h = self.interact_render.get_size()
            text_render = self.font.render(self.interact_message, True, (255, 255, 255))
            pygame.draw.rect(
                self.interact_render,
                pygame.Color("#212529"),
                ((0, 0), (text_w + 15, text_h + 15)),
                border_radius=15,
            )
            self.interact_render.blit(
                text_render,
                (
                    (self.inter_w - text_render.get_width()) / 2,
                    (self.inter_h - text_render.get_height()) / 2,
                ),
            )

            self.interact_render.set_alpha(200)

            # self.interact_render_rect = self.interact_render.get_rect(center=(0, 0))
            # self.interact_render_rect = self.interact_render.get_rect(center=(self.interact_rect.x + self.interact_rect.x / 2 - textw / 2 + 50, self.interact_rect.y + 19))
        else:
            self.on_interact = False

        e_pressed = False
        if joystick_input:
            e_pressed = eval(joystick_btn_dict["north-btn"])
        else:
            e_pressed = keys[pygame.K_e]

        if (
            self.on_interact
            and self.interact_message == "Pick up torch"
            and e_pressed
            and self.inventory.can_fill
        ):
            plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 12
            self.inventory.add_item("torch ")
        if (
            self.on_interact
            and self.interact_message == "Pick up wood"
            and e_pressed
            and self.inventory.can_fill
        ):
            plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 12
            self.inventory.add_item("wood ")
        if (
            self.on_interact
            and self.interact_message == "Harvest tomato"
            and e_pressed
            and self.inventory.can_fill
        ):
            plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 125
            self.inventory.add_item("tomato ")
        if (
            self.on_interact
            and self.interact_message == "Harvest flower"
            and e_pressed
            and self.inventory.can_fill
        ):
            plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 12
            self.inventory.add_item("flower ")
        if (
            self.on_interact
            and self.interact_message == "Mine stone (only with pickaxe)"
            and self.inventory.holding_pickaxe
        ):
            pygame.draw.rect(
                screen, pygame.Color("#212529"), self.stone_rect3, border_radius=26
            )
            pygame.draw.rect(
                screen, pygame.Color("#c1121f"), self.stone_rect2, border_radius=20
            )
            pygame.draw.rect(
                screen, pygame.Color("#0ead69"), self.stone_rect, border_radius=20
            )
            if e_pressed:
                if time.perf_counter() - self.cooldown > 0.8:
                    self.stone_rect.width -= (self.screen_size[0] / 4) / 4
                    self.cooldown = time.perf_counter()

                if time.perf_counter() - self.pickaxe_cooldown > 0.5:
                    self.pickaxe_frame = (self.pickaxe_frame + 1) % 2
                    self.pickaxe_cooldown = time.perf_counter()

            elif not e_pressed:
                self.stone_rect = pygame.Rect(
                    (self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                    (self.screen_size[0] / 4 - 16, 30),
                )
                self.stone_rect2 = pygame.Rect(
                    (self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                    (self.screen_size[0] / 4 - 16, 30),
                )
                self.stone_rect3 = pygame.Rect(
                    (self.screen_size[0] / 2 - self.screen_size[0] / 8, 100 - 8),
                    (self.screen_size[0] / 4, 46),
                )
                self.pickaxe_frame = 0
            if self.stone_rect.width <= 0:
                plants[self.player_tile[1] + 1, self.player_tile[0] + 1] = 12
                if random.randint(1, 3) == 1:
                    self.inventory.add_item("coal ")
                else:
                    self.inventory.add_item("stone ")
                self.pickaxe_frame = 0

        if (
            self.on_interact
            and self.interact_message == "Cut down tree (only with axe)"
            and self.inventory.holding_axe
        ):
            pygame.draw.rect(
                screen, pygame.Color("#212529"), self.stone_rect3, border_radius=26
            )
            pygame.draw.rect(
                screen, pygame.Color("#c1121f"), self.stone_rect2, border_radius=20
            )
            pygame.draw.rect(
                screen, pygame.Color("#0ead69"), self.stone_rect, border_radius=20
            )
            if e_pressed:
                # boom hp gaat omlaag :( <-- wtf | : ) <-- goed
                if time.perf_counter() - self.cooldown > 0.8:
                    self.stone_rect.width -= (self.screen_size[0] / 4) / 4
                    self.cooldown = time.perf_counter()
                    # make particles
                    for _ in range(15):
                        particle_x = 0
                        particle_y = 0
                        if self.direction == "RIGHT":
                            particle_x, particle_y = (
                                self.x - 1 + 35,
                                self.y - 1 + 5,
                            )
                        else:
                            particle_x, particle_y = (
                                self.x - 1 + 20 - 30,
                                self.y - 1 + 5,
                            )

                        particles.append(
                            HitParticle(particle_x, particle_y, pygame.Color("#422a0a"))
                        )

                # axe animatie
                if time.perf_counter() - self.axe_cooldown > 0.4:
                    self.axe_frame = (self.axe_frame + 1) % 2
                    self.axe_cooldown = time.perf_counter()

            elif not e_pressed:
                self.stone_rect = pygame.Rect(
                    (self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                    (self.screen_size[0] / 4 - 16, 30),
                )
                self.stone_rect2 = pygame.Rect(
                    (self.screen_size[0] / 2 - self.screen_size[0] / 8 + 8, 100),
                    (self.screen_size[0] / 4 - 16, 30),
                )
                self.stone_rect3 = pygame.Rect(
                    (self.screen_size[0] / 2 - self.screen_size[0] / 8, 100 - 8),
                    (self.screen_size[0] / 4, 46),
                )
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

        if (
            time.perf_counter() - self.update_frame_1 > 5
            and self.food_value > 800
            and self.health_value < 10
            and not self.poisoned
        ):
            self.update_frame_1 = time.perf_counter()
            self.health_value += 0.25

        if self.poisoned:
            self.hp_bar_color = pygame.Color("#588157")
            self.hp_icon = self.green_hp_icon
            # check if poison is over
            if self.poison_time + self.poison_duration <= time.perf_counter():
                self.poisoned = False
                self.hp_bar_color = pygame.Color("#ae2012")
                self.hp_icon = self.red_hp_icon
            else:
                self.health_value -= 0.01

        died = False

        if self.health_value <= 0:
            died = True
            self.health_value = 0

        return particles, died
