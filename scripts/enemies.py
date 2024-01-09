import pygame
import random
import time

from func import *
from scripts.ui import HealthBar


class Enemies:
    def __init__(self, spawn_rate, strength, speed):
        self.spawn_rate = spawn_rate
        self.strength = strength
        self.speed = speed
        # speed = {"zombie": random.randint(10,16)}
        self.max_spawn = {"zombie": 1000}
        self.is_night = False
        self.enemies = {
            "zombie": {
                "spawn_rate": self.spawn_rate["zombie"],
                "strength": self.strength["zombie"],
                "speed": self.speed["zombie"],
            }
        }
        self.scrollx, self.scrolly = 0, 0

        self.alive_enemies = []

        self.zombie_spawn_perf = -1  # perf counter for spawning enemy zombie

        self.imgs = {"zombie": {}}
        self.num_of_frames = {
            "zombie": {
                "idle": 7,
                "attack": 6,
                "special_attack": 21,
                "walk": 7,
                "die": 7,
            }
        }
        for enemy in list(self.num_of_frames.keys()):
            for load_img in list(
                self.num_of_frames[enemy].keys()
            ):  # list(self.num_of_frames.keys()) = ["idle", "attack", ...]
                for frame in range(self.num_of_frames[enemy][load_img]):
                    image = pygame.image.load(
                        f"./assets/{enemy}/{load_img}{frame+1}.png"
                    ).convert_alpha()
                    image_flip = pygame.transform.flip(image, True, False)

                    self.imgs[enemy][f"{load_img}{frame+1}right"] = image
                    self.imgs[enemy][f"{load_img}{frame+1}left"] = image_flip

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
            "rect": self.imgs[enemy_type]["idle1right"].get_rect(
                topleft=(spawn_x, spawn_y)
            ),  # change (500, 500) later
            "hp": 100,
            "strength": self.strength[enemy_type],
            "speed": self.speed[enemy_type],
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
            "health_bar": HealthBar((0, 0), (50, 5), 2, 100),
            "last_attack": -1,
        }

        add_enemy["x"] = float(add_enemy["rect"].x)
        add_enemy["y"] = float(add_enemy["rect"].y)

        self.alive_enemies.append(add_enemy)

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
                    screen.blit(
                        self.imgs[enemy["type"]][
                            f'{enemy["current_action"]}{enemy["current_animation_frame"]}{enemy["direction"]}'
                        ],
                        (blit_x, blit_y),
                    )
                    # if enemy["running_from_torch"]: #debug
                    #     pygame.draw.circle(screen, (255, 255, 255), (blit_x, blit_y), 5)

    def update(self, is_night, player, torch_locations_list, particles):
        self.is_night = is_night

        if is_night:
            if self.zombie_spawn_perf <= time.perf_counter():
                self.spawn_enemies(1, "zombie")
                self.zombie_spawn_perf = time.perf_counter() + 0.25

        for i, enemy in enumerate(self.alive_enemies):
            self.alive_enemies[i]["health_bar"].update(
                self.alive_enemies[i]["hp"],
                (
                    self.alive_enemies[i]["rect"].x - self.scrollx - (enemy["rect"].w / 2) + 12,
                    self.alive_enemies[i]["rect"].y - self.scrolly - 10,
                ),
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

            # getting hit
            if player.hitting:
                if (
                    get_distance(
                        player.x + 24,
                        player.y + 24,
                        self.alive_enemies[i]["rect"].x + 16,
                        self.alive_enemies[i]["rect"].y + 16,
                    )
                    < 25
                ):
                    self.alive_enemies[i]["last_attack"] = time.perf_counter()
                    self.alive_enemies[i]["hp"] -= random.randint(15, 25)
                    for _ in range(15):
                        particles.append(
                            HitParticle(
                                self.alive_enemies[i]["rect"].x + 16,
                                self.alive_enemies[i]["rect"].y + 16,
                                color="green",
                            )
                        )
                    if self.alive_enemies[i]["hp"] <= 0:
                        pygame.mixer.Sound.play(self.damage_sound)
                        for _ in range(50):
                            particles.append(
                                HitParticle(
                                    self.alive_enemies[i]["rect"].x + 16,
                                    self.alive_enemies[i]["rect"].y + 16,
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
                        self.alive_enemies[i]["x"] += enemy["walk_vx"]
                        self.alive_enemies[i]["y"] += enemy["walk_vy"]
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
