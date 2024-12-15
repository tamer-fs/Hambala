import pygame
import random
import time
import math
import copy

from func import *
from scripts.bow import *
from scripts.ui import HealthBar


class Enemies:
    def __init__(self, strength, speed, health):
        self.strength = strength
        self.spawn_rate = {
            "zombie": [100, 0],
            "zombie-big": [20, 0],
            "slime-green": [100, 1],
            "slime-red": [100, 1],
            "slime-white": [100, 1],
            "slime-blue": [100, 1],
        }
        self.speed = speed
        self.health = health
        # speed = {"zombie": random.randint(10,16)}
        self.max_spawn = {"zombie": 1000}  # nog niet gebruikt
        self.is_night = False
        self.enemies = {
            "zombie": {
                "strength": self.strength["zombie"],
                "speed": self.speed["zombie"],
                "hp": self.health["zombie"],
                "has-bow": False,
            },
            "zombie-big": {
                "strength": self.strength["zombie"],
                "speed": self.speed["zombie"],
                "hp": self.health["zombie"],
                "has-bow": False,
            },
            "slime-green": {
                "strength": self.strength["slime-green"],
                "speed": self.speed["slime-green"],
                "hp": self.health["slime-green"],
                "has-bow": False,
            },
            "slime-red": {
                "strength": self.strength["slime-red"],
                "speed": self.speed["slime-red"],
                "hp": self.health["slime-red"],
                "has-bow": False,
            },
            "slime-blue": {
                "strength": self.strength["slime-blue"],
                "speed": self.speed["slime-blue"],
                "hp": self.health["slime-blue"],
                "has-bow": False,
            },
            "slime-white": {
                "strength": self.strength["slime-white"],
                "speed": self.speed["slime-white"],
                "hp": self.health["slime-white"],
                "has-bow": True,
                "bow-size": 25,
            },
        }

        """
        Slime types:
        Green: Standard slappe poep luie blobbel
        Red: Ietsjes sneller en meer damage
        Blue: Heel snel maar slap
        White: Heel langzaam en sterk en een boog
        """

        self.enemies_size = {
            "zombie": (32, 32),
            "zombie-big": (60, 60),
            "slime-green": (32, 32),
            "slime-red": (25, 25),
            "slime-blue": (32, 32),
            "slime-white": (40, 40),
        }
        self.scrollx, self.scrolly = 0, 0

        self.alive_enemies = []

        self.zombie_spawn_perf = -1  # perf counter for spawning enemy zombie

        self.imgs = {
            "zombie": {},
            "zombie-big": {},
            "slime-green": {},
            "slime-red": {},
            "slime-blue": {},
            "slime-white": {},
        }
        self.num_of_frames = {
            "zombie": {
                "idle": 7,
                "attack": 6,
                "special_attack": 21,
                "walk": 7,
                "die": 7,
            },
            "zombie-big": {
                "idle": 7,
                "attack": 6,
                "special_attack": 21,
                "walk": 7,
                "die": 7,
            },
            "slime-green": {
                "front": 2,
                "left": 2,
                "right": 2,
                "up": 2,
                "idle": 2,
                "attack": 2,
                "special_attack": 2,
                "walk": 2,
                "die": 2,
            },
            "slime-red": {
                "front": 2,
                "left": 2,
                "right": 2,
                "up": 2,
                "idle": 2,
                "attack": 2,
                "special_attack": 2,
                "walk": 2,
                "die": 2,
            },
            "slime-blue": {
                "front": 2,
                "left": 2,
                "right": 2,
                "up": 2,
                "idle": 2,
                "attack": 2,
                "special_attack": 2,
                "walk": 2,
                "die": 2,
            },
            "slime-white": {
                "front": 2,
                "left": 2,
                "right": 2,
                "up": 2,
                "idle": 2,
                "attack": 2,
                "special_attack": 2,
                "walk": 2,
                "die": 2,
            },
        }
        for enemy in list(self.num_of_frames.keys()):
            for load_img in list(
                self.num_of_frames[enemy].keys()
            ):  # list(self.num_of_frames.keys()) = ["idle", "attack", ...]
                for frame in range(self.num_of_frames[enemy][load_img]):
                    if enemy[:5] == "slime":
                        if load_img in ["front", "left", "right", "up"]:
                            enemy_img = enemy
                            slime_color = enemy.split("-")[1]

                            image = pygame.image.load(
                                f"./assets/slimes/{slime_color}/{load_img}{frame+1}.png"
                            ).convert_alpha()

                            image = pygame.transform.scale(
                                image, self.enemies_size[enemy]
                            )

                            self.imgs[enemy][f"{load_img}{frame+1}"] = image
                    else:
                        if "-" in enemy:
                            enemy_img = enemy.split("-")[0]
                        else:
                            enemy_img = enemy

                        image = pygame.image.load(
                            f"./assets/{enemy_img}/{load_img}{frame+1}.png"
                        ).convert_alpha()
                        image_flip = pygame.transform.flip(image, True, False)
                        image = pygame.transform.scale(image, self.enemies_size[enemy])
                        image_flip = pygame.transform.scale(
                            image_flip, self.enemies_size[enemy]
                        )

                        self.imgs[enemy][f"{load_img}{frame+1}right"] = image
                        self.imgs[enemy][f"{load_img}{frame+1}left"] = image_flip

        # print(self.imgs)

        # self.imgs[enemy][load_img][frame] = pygame.image.load(f'./assets/{enemy}{load_img}{frame}.png').convert_alpha()
        # self.imgs[enemy][load_img][f'{frame}right'] = pygame.transform.flip(pygame.image.load(f'./assets/{enemy}{load_img}{frame}.png').convert_alpha(), True, False)
        self.damage_sound = pygame.mixer.Sound("assets/sounds/damage.wav")

    def spawn_enemies(self, enemy_count, enemy_type):
        spawn_side = random.choice(["top", "bottom", "left", "right"])
        spawn_x, spawn_y = 0, 0
        if spawn_side == "top":
            spawn_x = random.randint(50, 150 * 16 - 50)
            spawn_y = random.randint(25, 400)
        elif spawn_side == "bottom":
            spawn_x = random.randint(50, 150 * 16 - 50)
            spawn_y = random.randint(150 * 16 - 400, 150 * 16 - 25)
        elif spawn_side == "left":
            spawn_x = random.randint(50, 100)
            spawn_y = random.randint(25, 150 * 16 - 25)
        elif spawn_side == "right":
            spawn_x = random.randint(150 * 16 - 400, 150 * 16 - 25)
            spawn_y = random.randint(25, 150 * 16 - 25)

        add_enemy = {
            "type": enemy_type,
            "direction": random.choice(["right", "left"]),
            "rect": self.imgs[enemy_type][
                list(self.imgs[enemy_type].keys())[0]
            ].get_rect(
                topleft=(spawn_x, spawn_y)
            ),  # change (500, 500) later
            "hp": random.randint(
                self.health[enemy_type][0], self.health[enemy_type][1]
            ),
            "has_bow": self.enemies[enemy_type]["has-bow"],
            "strength": random.randint(
                self.strength[enemy_type][0], self.strength[enemy_type][1]
            ),
            "speed": random.randint(
                self.speed[enemy_type][0], self.speed[enemy_type][1]
            )
            * 5,
            "current_animation_frame": random.randint(1, 3),
            "current_action": "walk",
            "next_frame_perf": -1,
            "start_attack_perf": -1,  # perf_counter for when enemy starts (normal) attack
            "start_special_attack_perf": -1,  # perf counter for when enemy starts special attack (if none for enemy, skip)
            "chasing_player": False,
            "walk_vx": 0,
            "walk_vy": 0,
            "walking": False,
            "start_walking_perf": time.perf_counter() + random.randint(3, 5),
            "stop_walking_perf": time.perf_counter() + random.randint(7, 9),
            "following_player": False,
            "near_torch": False,
            "range_torch_locations": [],  # torch locations that are in range of the enemy
            "running_from_torch": False,
            "health_bar": HealthBar(
                (0, 0),
                ((self.enemies_size[enemy_type][0]), 5),
                2,
                random.randint(self.health[enemy_type][0], self.health[enemy_type][1]),
            ),
            "last_attack": -1,
            "attack_cooldown": -1,
            "attack_cooldown_duration": 2,
        }

        if add_enemy["has_bow"]:
            add_enemy["bow"] = Bow(
                size=self.enemies[enemy_type]["bow-size"], unlimited_arrows=True
            )
            add_enemy["bow_shoot_timer"] = -1
            add_enemy["bow_shoot_delay"] = random.randint(0, 6)
            add_enemy["charge_started"] = False
            add_enemy["charge_delay_timer"] = -1
            add_enemy["charge_delay"] = random.randint(2, 5)
            add_enemy["charge_timer_set"] = False

        add_enemy["x"] = float(add_enemy["rect"].x)
        add_enemy["y"] = float(add_enemy["rect"].y)

        self.alive_enemies.append(add_enemy)

    def return_enemies_list(self):
        return_list = []
        for enemy in self.alive_enemies:
            enemy_dict = {}
            for key in enemy.keys():

                if key == "rect":
                    rect = enemy["rect"]
                    enemy_dict["rect"] = [rect.x, rect.y, rect.w, rect.h]
                elif key == "health_bar":
                    enemy_dict["health_bar"] = "<health bar achtig item, wtf sirieus?>"
                elif key == "bow":
                    if enemy["has_bow"]:
                        enemy_dict["bow"] = "<boog iets dix-huit dix-neuf vingt>"
                else:
                    enemy_dict[key] = enemy[key]

            return_list.append(enemy_dict)

        return return_list

    def convert_enemies_json(self, enemies_json_list):
        self.alive_enemies = []
        for enemy_dict in enemies_json_list:

            get_dict = copy.deepcopy(enemy_dict)
            return_dict = copy.deepcopy(enemy_dict)

            for key in return_dict.keys():
                if key == "rect":
                    rect = get_dict["rect"]
                    return_dict["rect"] = pygame.Rect(rect)
                elif key == "health_bar":
                    return_dict["health_bar"] = HealthBar(
                        (0, 0),
                        ((self.enemies_size[get_dict["type"]][0]), 5),
                        2,
                        random.randint(
                            self.health[get_dict["type"]][0],
                            self.health[get_dict["type"]][1],
                        ),
                    )

                elif key == "bow":
                    if get_dict["has_bow"]:
                        return_dict["bow"] = Bow(
                            size=self.enemies[get_dict["type"]]["bow-size"],
                            unlimited_arrows=True,
                        )
                    else:
                        continue
                else:
                    return_dict[key] = get_dict[key]

            self.alive_enemies.append(copy.deepcopy(return_dict))

    def draw_enemies(self, screen, scrollx, scrolly):
        self.scrollx, self.scrolly = scrollx, scrolly
        width, height = screen.get_size()
        for i, enemy in enumerate(self.alive_enemies):
            blit_x = round(enemy["x"] - scrollx)
            blit_y = round(enemy["y"] - scrolly)
            if time.perf_counter() - self.alive_enemies[i]["last_attack"] < 10:
                self.alive_enemies[i]["health_bar"].draw(
                    screen, "black", "darkgray", "green", 2, 2
                )

            if blit_x > 0 - 100 and blit_x < width:
                if blit_y > 0 - 100 and blit_y < height:
                    if enemy["type"][:5] == "slime":
                        screen.blit(
                            self.imgs[enemy["type"]][
                                f'{enemy["direction"]}{enemy["current_animation_frame"]}'
                            ],
                            (blit_x, blit_y),
                        )
                    elif enemy["type"][:6] == "zombie":
                        screen.blit(
                            self.imgs[enemy["type"]][
                                f'{enemy["current_action"]}{enemy["current_animation_frame"]}{enemy["direction"]}'
                            ],
                            (blit_x, blit_y),
                        )

            if self.alive_enemies[i]["has_bow"]:
                self.alive_enemies[i]["bow"].draw(screen, scrollx, scrolly)
                # if enemy["running_from_torch"]: #debug
                #     pygame.draw.circle(screen, (255, 255, 255), (blit_x, blit_y), 5)

    def update(
        self,
        is_night,
        player,
        torch_locations_list,
        particles,
        night_count,
        player_bow,
        dt,
    ):
        self.is_night = is_night

        spawn_list = []
        for spawn_enemy in self.spawn_rate:
            if night_count >= self.spawn_rate[spawn_enemy][1]:
                for amount in range(self.spawn_rate[spawn_enemy][0]):
                    spawn_list.append(spawn_enemy)

        if is_night:
            if self.zombie_spawn_perf <= time.perf_counter():
                self.spawn_enemies(1, random.choice(spawn_list))
                self.zombie_spawn_perf = time.perf_counter() + 0.25

        for i, enemy in enumerate(self.alive_enemies):
            self.alive_enemies[i]["health_bar"].update(
                self.alive_enemies[i]["hp"],
                (
                    self.alive_enemies[i]["rect"].x - self.scrollx,
                    # - (enemy["rect"].w / 2)
                    # + (self.enemies_size[self.alive_enemies[i]["type"]][0]/2),
                    self.alive_enemies[i]["rect"].y - self.scrolly - 10,
                ),
            )

            if (
                random.randint(1, 10) == 1 and self.alive_enemies[i]["type"] == "zombie"
            ) or (
                random.randint(1, 5) == 1
                and self.alive_enemies[i]["type"] == "zombie-big"
            ):
                particles.append(
                    HitParticle(
                        self.alive_enemies[i]["rect"].x
                        + (self.enemies_size[self.alive_enemies[i]["type"]][0] / 2)
                        + random.randint(-10, 10),
                        self.alive_enemies[i]["rect"].y
                        + (self.enemies_size[self.alive_enemies[i]["type"]][1] / 2)
                        + random.randint(-20, 0),
                        color=(128, 137, 99),
                        up=True,
                    )
                )

            detected_torch = False
            self.alive_enemies[i]["range_torch_locations"] = []
            for torch_loc in torch_locations_list:
                if (
                    get_distance(
                        torch_loc[0] * 16,
                        torch_loc[1] * 16,
                        self.alive_enemies[i]["rect"].x,
                        self.alive_enemies[i]["rect"].y,
                    )
                    < 200
                ):
                    detected_torch = True
                    self.alive_enemies[i]["range_torch_locations"].append(
                        (torch_loc[0] * 16, torch_loc[1] * 16)
                    )

            self.alive_enemies[i]["near_torch"] = detected_torch

            # zombie hitting player
            if get_distance(
                player.x + 24,
                player.y + 24,
                self.alive_enemies[i]["rect"].x
                + (self.enemies_size[self.alive_enemies[i]["type"]][0] / 2),
                self.alive_enemies[i]["rect"].y
                + (self.enemies_size[self.alive_enemies[i]["type"]][1] / 2),
            ) < (self.enemies_size[self.alive_enemies[i]["type"]][1] / 2):
                if (
                    time.perf_counter() - self.alive_enemies[i]["attack_cooldown"]
                    > self.alive_enemies[i]["attack_cooldown_duration"]
                ):
                    self.alive_enemies[i]["attack_cooldown"] = time.perf_counter()
                    player.health_value -= math.ceil(
                        self.alive_enemies[i]["strength"] / 10
                    )
                    player.health_value = max(0, player.health_value)
                    for _ in range(25):
                        particles.append(
                            HitParticle(
                                self.alive_enemies[i]["rect"].x
                                + (
                                    self.enemies_size[self.alive_enemies[i]["type"]][0]
                                    / 2
                                ),
                                self.alive_enemies[i]["rect"].y
                                + (
                                    self.enemies_size[self.alive_enemies[i]["type"]][1]
                                    / 2
                                ),
                                color="red",
                            )
                        )

            if self.alive_enemies[i]["has_bow"]:
                angle = 0
                enemy = self.alive_enemies[i]
                rect = self.alive_enemies[i]["rect"]

                if (
                    get_distance(
                        player.x + 24,
                        player.y + 24,
                        self.alive_enemies[i]["rect"].x
                        + (self.enemies_size[self.alive_enemies[i]["type"]][0] / 2),
                        self.alive_enemies[i]["rect"].y
                        + (self.enemies_size[self.alive_enemies[i]["type"]][1] / 2),
                    )
                    < 400
                ):
                    # boog mikken
                    player_x, player_y = player.x, player.y
                    player_dx = player_x - rect.x
                    player_dy = player_y - rect.y
                    player_dx = 0.01 if player_dx == 0 else player_dx
                    player_dy = 0.01 if player_dy == 0 else player_dy
                    tan_angle = player_dy / player_dx
                    angle = math.degrees(math.atan(tan_angle))
                    if abs(player_dx) != player_dx:
                        angle += 180

                    # boog schieten
                    if enemy["charge_started"] == False:
                        if enemy["charge_timer_set"] == False:
                            enemy["charge_delay_timer"] = time.perf_counter()
                            enemy["charge_timer_set"] = True
                        if (
                            time.perf_counter() - enemy["charge_delay_timer"]
                            > enemy["charge_delay"]
                        ):
                            enemy["bow"].start_charge()
                            enemy["charge_started"] = True
                            enemy["bow_shoot_timer"] = time.perf_counter()

                    if (
                        time.perf_counter() - enemy["bow_shoot_timer"]
                        > enemy["bow_shoot_delay"]
                        and enemy["charge_started"] == True
                    ):
                        enemy["bow"].shoot_arrow()
                        enemy["charge_started"] = False
                        enemy["bow_shoot_delay"] = random.randint(0, 6)
                        enemy["charge_timer_set"] = False

                enemy["bow"].update(
                    self.alive_enemies[i]["rect"].x + rect.w / 2,
                    self.alive_enemies[i]["rect"].y + rect.h / 2,
                    round(angle),
                    dt,
                )

            # arrow (by player) hitting zombie
            for arrow in player_bow.arrow_list:
                if (
                    self.alive_enemies[i]["rect"].colliderect(arrow.rect)
                    and arrow.can_damage
                ):
                    arrow.can_damage = False
                    self.alive_enemies[i]["health_bar"].damage()
                    self.alive_enemies[i]["last_attack"] = time.perf_counter()
                    self.alive_enemies[i]["hp"] -= arrow.damage
                    for _ in range(15):
                        particles.append(
                            HitParticle(
                                self.alive_enemies[i]["rect"].x
                                + (
                                    self.enemies_size[self.alive_enemies[i]["type"]][0]
                                    / 2
                                ),
                                self.alive_enemies[i]["rect"].y
                                + (
                                    self.enemies_size[self.alive_enemies[i]["type"]][1]
                                    / 2
                                ),
                                color="green",
                            )
                        )
                    if self.alive_enemies[i]["hp"] <= 0:
                        pygame.mixer.Sound.play(self.damage_sound)
                        for _ in range(50):
                            particles.append(
                                HitParticle(
                                    self.alive_enemies[i]["rect"].x
                                    + (
                                        self.enemies_size[
                                            self.alive_enemies[i]["type"]
                                        ][0]
                                        / 2
                                    ),
                                    self.alive_enemies[i]["rect"].y
                                    + (
                                        self.enemies_size[
                                            self.alive_enemies[i]["type"]
                                        ][1]
                                        / 2
                                    ),
                                    color="green",
                                )
                            )
                        self.alive_enemies.remove(self.alive_enemies[i])

            # enemy with bow hitting player
            if self.alive_enemies[i]["has_bow"]:
                for arrow in self.alive_enemies[i]["bow"].arrow_list:
                    if (
                        arrow.rect.colliderect(pygame.Rect(player.x, player.y, 48, 48))
                        and arrow.can_damage
                    ):
                        arrow.can_damage = False
                        player.health_value -= round(arrow.damage / 12)
                        for _ in range(15):
                            particles.append(
                                HitParticle(
                                    player.x + (48 / 2),
                                    player.y + (48 / 2),
                                    color="red",
                                )
                            )

            # player hitting zombie
            if player.hitting:
                if get_distance(
                    player.x + 24,
                    player.y + 24,
                    self.alive_enemies[i]["rect"].x
                    + (self.enemies_size[self.alive_enemies[i]["type"]][0] / 2),
                    self.alive_enemies[i]["rect"].y
                    + (self.enemies_size[self.alive_enemies[i]["type"]][1] / 2),
                ) < (self.enemies_size[self.alive_enemies[i]["type"]][1]):
                    self.alive_enemies[i]["health_bar"].damage()
                    self.alive_enemies[i]["last_attack"] = time.perf_counter()
                    self.alive_enemies[i]["hp"] -= random.randint(30, 50)
                    for _ in range(15):
                        particles.append(
                            HitParticle(
                                self.alive_enemies[i]["rect"].x
                                + (
                                    self.enemies_size[self.alive_enemies[i]["type"]][0]
                                    / 2
                                ),
                                self.alive_enemies[i]["rect"].y
                                + (
                                    self.enemies_size[self.alive_enemies[i]["type"]][1]
                                    / 2
                                ),
                                color="green",
                            )
                        )
                    if self.alive_enemies[i]["hp"] <= 0:
                        pygame.mixer.Sound.play(self.damage_sound)
                        for _ in range(50):
                            particles.append(
                                HitParticle(
                                    self.alive_enemies[i]["rect"].x
                                    + (
                                        self.enemies_size[
                                            self.alive_enemies[i]["type"]
                                        ][0]
                                        / 2
                                    ),
                                    self.alive_enemies[i]["rect"].y
                                    + (
                                        self.enemies_size[
                                            self.alive_enemies[i]["type"]
                                        ][1]
                                        / 2
                                    ),
                                    color="green",
                                )
                            )
                        self.alive_enemies.remove(self.alive_enemies[i])

                    player.hitting = False

            # walk animation
            if enemy["next_frame_perf"] + 0.1 < time.perf_counter():
                self.alive_enemies[i]["next_frame_perf"] = time.perf_counter()
                self.alive_enemies[i]["current_animation_frame"] = (
                    enemy["current_animation_frame"]
                ) % self.num_of_frames[enemy["type"]][enemy["current_action"]] + 1

            if enemy["near_torch"] and not enemy["running_from_torch"]:
                self.alive_enemies[i]["walking"] = False
                self.alive_enemies[i]["following_player"] = False

            if not enemy["near_torch"] and enemy["running_from_torch"]:
                self.alive_enemies[i]["running_from_torch"] = False
                self.alive_enemies[i]["walking"] = False

            if not enemy["walking"] and not enemy["following_player"]:
                self.alive_enemies[i][
                    "start_walking_perf"
                ] = time.perf_counter() + random.randint(3, 20)
                self.alive_enemies[i]["stop_walking_perf"] = (
                    time.perf_counter()
                    + random.randint(1, 3)
                    + self.alive_enemies[i]["start_walking_perf"]
                )

                if (
                    self.alive_enemies[i]["near_torch"]
                    and not self.alive_enemies[i]["running_from_torch"]
                ):
                    if len(self.alive_enemies[i]["range_torch_locations"]) > 1:
                        torch_x = []
                        torch_y = []
                        for loc in enemy["range_torch_locations"]:
                            torch_x.append(loc[0])
                            torch_y.append(loc[1])

                        lantern_loc = (
                            sum(torch_x) / len(torch_x),
                            sum(torch_y) / len(torch_y),
                        )
                    else:
                        lantern_loc = self.alive_enemies[i]["range_torch_locations"][0]

                    self_x = self.alive_enemies[i]["rect"].x
                    self_y = self.alive_enemies[i]["rect"].y
                    self_w = self.alive_enemies[i]["rect"].w
                    self_h = self.alive_enemies[i]["rect"].h

                    x_diff = self_x - lantern_loc[0]
                    y_diff = self_y - lantern_loc[1]

                    max_steps = round(
                        get_distance(
                            self.alive_enemies[i]["rect"].x,
                            self.alive_enemies[i]["rect"].y,
                            lantern_loc[0],
                            lantern_loc[1],
                        )
                        * 1
                    )

                    lantern_x, lantern_y = lantern_loc[0] + 8, lantern_loc[1] + 8
                    self_x, self_y = self_x + (self_w / 2), self_y + (self_h / 2)
                    x_diff = 0
                    y_diff = 0
                    x_diff = lantern_x - self_x
                    y_diff = lantern_y - self_y
                    step_x = min(x_diff / max_steps, 2.5)
                    step_y = min(y_diff / max_steps, 2.5)

                    walk_vx, walk_vy = step_x, step_y

                    self.alive_enemies[i]["walk_vx"] = walk_vx * -1
                    self.alive_enemies[i]["walk_vy"] = walk_vy * -1

                    # print(self.alive_enemies[i]["walk_vx"], self.alive_enemies[i]["walk_vy"])
                    # print("walked away from torch")

                    self.alive_enemies[i]["walking"] = True
                    self.alive_enemies[i]["current_action"] = "walk"
                    self.alive_enemies[i]["running_from_torch"] = True
                    self.alive_enemies[i]["start_walking_perf"] = (
                        time.perf_counter() - 0.1
                    )
                    self.alive_enemies[i][
                        "stop_walking_perf"
                    ] = time.perf_counter() + random.randint(3, 5)
                    self.alive_enemies[i]["following_player"] = False

                else:
                    self.alive_enemies[i]["walk_vx"] = random.randint(-8, 8) / 10
                    self.alive_enemies[i]["walk_vy"] = random.randint(-8, 8) / 10

                    self.alive_enemies[i]["walking"] = True
                    self.alive_enemies[i]["current_action"] = "idle"

            else:
                if time.perf_counter() >= enemy["start_walking_perf"]:
                    if time.perf_counter() <= enemy["stop_walking_perf"]:
                        self.alive_enemies[i]["x"] += (
                            enemy["walk_vx"] * (enemy["speed"] / 100) * dt
                        )
                        self.alive_enemies[i]["y"] += (
                            enemy["walk_vy"] * (enemy["speed"] / 100) * dt
                        )
                        self.alive_enemies[i]["current_action"] = "walk"
                        if enemy["walk_vx"] > 0:
                            self.alive_enemies[i]["direction"] = "right"
                        else:
                            self.alive_enemies[i]["direction"] = "left"
                    else:
                        self.alive_enemies[i]["walking"] = False

                else:
                    self.alive_enemies[i]["current_action"] = "idle"

            self.alive_enemies[i]["rect"].x = round(enemy["x"])
            self.alive_enemies[i]["rect"].y = round(enemy["y"])

            if (
                get_distance(
                    self.alive_enemies[i]["rect"].x,
                    self.alive_enemies[i]["rect"].y,
                    player.x,
                    player.y,
                )
                < 300
            ) and not self.alive_enemies[i]["running_from_torch"]:
                self.alive_enemies[i]["following_player"] = True

                # how many steps
                max_steps = round(
                    get_distance(
                        self.alive_enemies[i]["rect"].x,
                        self.alive_enemies[i]["rect"].y,
                        player.x,
                        player.y,
                    )
                    * 2
                )

                self_x = self.alive_enemies[i]["rect"].x
                self_y = self.alive_enemies[i]["rect"].y
                self_w = self.alive_enemies[i]["rect"].w
                self_h = self.alive_enemies[i]["rect"].h

                # get distance between player & enemy
                x_diff = self_x - player.x
                y_diff = self_y - player.y

                player_x, player_y = player.x + 24, player.y + 24
                self_x, self_y = self_x + (self_w / 2), self_y + (self_h / 2)
                x_diff = 0
                y_diff = 0
                x_diff = player_x - self_x
                y_diff = player_y - self_y
                step_x = min(x_diff / max_steps, 2.5)
                step_y = min(y_diff / max_steps, 2.5)

                walk_vx, walk_vy = step_x, step_y

                self.alive_enemies[i]["walk_vx"] = walk_vx
                self.alive_enemies[i]["walk_vy"] = walk_vy

            elif (
                get_distance(
                    self.alive_enemies[i]["rect"].x,
                    self.alive_enemies[i]["rect"].y,
                    player.x,
                    player.y,
                )
                > 600
                and self.alive_enemies[i]["following_player"]
                and not self.alive_enemies[i]["running_from_torch"]
            ):
                self.alive_enemies[i]["walk_vx"] = 0
                self.alive_enemies[i]["walk_vy"] = 0
                self.alive_enemies[i]["following_player"] = False
                self.alive_enemies[i]["current_action"] = "idle"
                self.alive_enemies[i]["walking"] = False
                self.alive_enemies[i][
                    "start_walking_perf"
                ] = time.perf_counter() + random.randint(3, 20)

        return particles
