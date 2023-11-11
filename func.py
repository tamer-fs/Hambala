import math

import pygame
import numpy
import random
import os
import time
import matplotlib
import json
import copy
from scripts.particle import *

pygame.mixer.init()

with open("controller_type.txt") as f:
    controller_type = f.read()

joystick_btn_dict = {}
if controller_type != "":
    with open("joystick_btn_dict.json") as f:
        joystick_btn_dict = json.load(f)
        joystick_btn_dict = joystick_btn_dict[controller_type]
        print(joystick_btn_dict)


def get_distance(x1, y1, x2, y2):
    c2 = math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2)
    c = math.sqrt(c2)
    return c


def place_item(plants, item_id, tile_x, tile_y):
    if not plants[tile_y, tile_x] in [61, 62, 48, 49]:  # prevent placement on tree tile
        plants[tile_y, tile_x] = item_id
        return plants
    

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
        self.player = None
        self.damage_sound = pygame.mixer.Sound("assets/sounds/damage.wav")
        self.drop_item = {
            "sheep": "meat ",
            "sheepbrown": "meat ",
            "wolfblue": "meat ",
            "wolfblack": "meat ",
            "wolfbluebrown": "meat ",
            "wolfwhite": "meat ",
            "bearblue": "meat ",
            "bearbrown": "meat ",
            "ratwhite": "rat's tail ",
        }
        self.attack_delay = 2

        self.pic_dict = {}
        self.load_images = [
            "sheep",
            "sheepbrown",
            "bearblue",
            "bearbrown",
            "wolfblue",
            "wolfwhite",
            "wolfbluebrown",
            "wolfblack",
            "ratwhite",
        ]
        for load_image in self.load_images:
            for direction in ["front", "right", "back", "left"]:
                for frame in range(1, 5):
                    if not direction == "left":
                        image = pygame.image.load(
                            f"assets/{load_image}/{load_image}{direction}{str(frame)}.png"
                        ).convert_alpha()
                    else:
                        image = pygame.image.load(
                            f"assets/{load_image}/{load_image}right{str(frame)}.png"
                        ).convert_alpha()
                        image = pygame.transform.flip(image, True, False)

                    self.pic_dict[
                        f"{load_image}{direction}{str(frame)}tiny"
                    ] = pygame.transform.smoothscale(image, (14, 14))

                    self.pic_dict[f"{load_image}{direction}{str(frame)}small"] = image

                    self.pic_dict[
                        f"{load_image}{direction}{str(frame)}big"
                    ] = pygame.transform.scale(image, (18, 18))

        self.rect = None
        self.animal_dict = {}

        spawn_list = []
        spawn_freq = {
            "sheep": 60,
            "sheepbrown": 10,
            "wolfblue": 15,
            "wolfblack": 30,
            "wolfbluebrown": 20,
            "wolfwhite": 12,
            "bearblue": 5,
            "bearbrown": 30,
            "ratwhite": 9,
        }
        for animal in spawn_freq.keys():
            for _ in range(spawn_freq[animal]):
                spawn_list.append(animal)

        group_count = random.randint(15, 20)
        group_list = []
        for group_loop in range(group_count):
            group_list.append(
                (
                    random.randint(100, 2300),
                    random.randint(100, 2300),
                    random.choice(spawn_list),
                )
            )  # x, y, animal_type

        for x in range(self.max_spawn):
            size = random.choice(["small", "big"])
            group = random.randint(0, group_count - 1)
            rect = self.pic_dict["sheepright1small"].get_rect(
                topleft=(
                    group_list[group][0] + random.randint(-250, 250),
                    group_list[group][1] + random.randint(-250, 250),
                )
            )

            if group_list[group][2] == "ratwhite":
                self.spawn_animal(rect, "tiny", group_list[group][2], x)
            else:
                self.spawn_animal(rect, size, group_list[group][2], x)

    def spawn_animal(self, rect, size, animal_type, x):
        if "bear" in animal_type:
            hp = 180
        elif "rat" in animal_type:
            hp = 60
        else:
            hp = random.randint(100, 115)

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
                    hp,  # hp 15
                    False,  # set target 16
                    0,  # animal start attack 17
                    time.perf_counter(),  # animal kill/attack player 18
                    random.randint(2, 4),  # damage to player 19
                    False,  # animal boos 20
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

            if (
                animal_walking and time.perf_counter() - animal_frame_timer > 0.2
            ):  # change to next frame
                animal[11] = (animal_frame + 1) % 4
                animal[12] = time.perf_counter()

            if not animal_walking:
                animal[11] = 1

            screen.blit(
                self.pic_dict[
                    f"{animal_type}{animal_draw_direction}{animal[11] + 1}{animal_size}"
                ],
                (animal_rect.x - scrollx, animal_rect.y - scrolly),
            )

    def create_walk_plan(
        self, max_steps, walking_speed, to_player=False, animal_rect=None
    ):
        return_list = []
        if to_player == False:
            waypoint = random.choice(["tl", "tr", "l", "r", "bl", "br", "b", "t"])
            direction = ""
            walk_speed = walking_speed
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
        else:
            # kijken of beer x groter kleiner dan player x en hetzelfde met y
            player_x, player_y = self.player.x + 24, self.player.y + 24
            animal_x, animal_y = animal_rect.x + (animal_rect.w / 2), animal_rect.y + (
                animal_rect.h / 2
            )
            x_diff = 0
            y_diff = 0
            x_diff = player_x - animal_x
            y_diff = player_y - animal_y
            step_x = min(x_diff / max_steps, 2.5)
            step_y = min(y_diff / max_steps, 2.5)
            for x in range(max_steps):
                return_list.append((round(step_x), round(step_y)))

            if abs(x_diff) > abs(y_diff):
                if abs(step_x) == step_x:  # is positive
                    direction = "right"
                else:
                    direction = "left"
            else:
                if abs(step_y) == step_y:
                    direction = "front"
                else:
                    direction = "back"

        return return_list, direction

    def set_inventory(self, inventory):
        self.inventory = inventory

    def update(self, plants, player, particles):
        animal_delete_list = []
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
            animal_break_time = animal[9]
            animal_draw_direction = animal[10]
            hungry = animal[14]
            player = player
            animal_hp = animal[15]
            animal_set_target = animal[16]
            animal_start_attack = animal[17]
            # perf counter for animal attacking player
            animal_attack_player = animal[18]
            animal_damage = animal[19]  # amount of damage animal does

            if time.perf_counter() - animal_perf > animal_break_time:
                if animal_walking:
                    animal[4] = False
                else:
                    animal[4] = True
                    animal[6] = random.randint(30, 150)
                    animal[7], animal[10] = self.create_walk_plan(animal[6], 0.5)
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
                if (
                    not animal_rect.y < -150 * 16 - 32
                    and not animal_rect.y > 150 * 16 - 32
                ):
                    if plants[on_tile[1] + 1, on_tile[0] + 1] in [127, 11] and hungry:
                        plants[on_tile[1] + 1, on_tile[0] + 1] = 0

            if (
                get_distance(animal_rect.x, animal_rect.y, player.x + 16, player.y + 16)
                < 35
            ):
                if "rat" in animal_type:
                    player.poisoned = True
                    player.poison_time = time.perf_counter()

                if player.hitting:
                    if "bear" in animal_type:
                        animal[18] = time.perf_counter() + self.attack_delay
                        animal[20] = True
                    pygame.mixer.Sound.play(self.damage_sound)
                    # maak particles
                    for _ in range(15):
                        particles.append(HitParticle(animal[0].x, animal[0].y))
                    animal[4] = True
                    animal[6] = random.randint(300, 350)
                    if animal_type in ["bearbrown", "bearblue"]:
                        animal[17] = time.perf_counter() + 1
                        animal[4] = False
                    else:
                        animal[7], animal[10] = self.create_walk_plan(
                            animal[6], 1.2, False
                        )
                    animal[15] -= random.randint(30, 40)
                    animal_rect.y += random.randint(-5, 5)
                    animal_rect.x += random.randint(-5, 5)
                    player.hitting = False

            if (
                get_distance(animal_rect.x, animal_rect.y, player.x + 16, player.y + 16)
                < 500
            ):
                if animal[17] <= time.perf_counter() and animal[17] != 0:
                    animal[4] = True
                    animal[6] = random.randint(10, 20)
                    animal[7], animal[10] = self.create_walk_plan(
                        animal[6], 1.2, True, animal_rect=animal[0]
                    )
            else:
                animal[4] = False

            # bear attack player
            if animal[20]:
                if (
                    get_distance(
                        animal_rect.x, animal_rect.y, player.x + 16, player.y + 16
                    )
                    < 30
                ):
                    if time.perf_counter() - animal[18] > 1.5:
                        animal[18] = time.perf_counter()
                        player.health_value -= animal_damage
                        player.health_value = max(0, player.health_value)
                        pygame.mixer.Sound.play(self.damage_sound)
                        for _ in range(15):
                            particles.append(HitParticle(player.x, player.y))

            if animal_hp <= 0:
                animal_delete_list.append(animal_key)
                if "rat" in animal_type:
                    player.poisoned = True
                    player.poison_time = time.perf_counter()
                    self.inventory.dropped_items[len(self.inventory.dropped_items)] = [
                        self.drop_item[animal_type],
                        animal_rect.x + random.choice([-60, 60, 55, -55]),
                        animal_rect.y + random.choice([-60, 60, 55, -55]),
                        time.perf_counter(),
                    ]
                else:
                    for _ in range(random.randint(1, 2)):
                        self.inventory.dropped_items[
                            len(self.inventory.dropped_items)
                        ] = [
                            self.drop_item[animal_type],
                            animal_rect.x + random.choice([-60, 60, 55, -55]),
                            animal_rect.y + random.choice([-60, 60, 55, -55]),
                            time.perf_counter(),
                        ]
                for _ in range(30):
                    particles.append(HitParticle(animal[0].x, animal[0].y))

        for delete_animal in sorted(animal_delete_list, reverse=True):
            self.animal_dict.pop(delete_animal)

        return particles



def load_img():
    images = {}

    for x in range(138):
        if x > 99:
            tile_num = str(x)
        elif x > 9:
            tile_num = f"0{x}"
        else:
            tile_num = f"00{x}"

        images[f"tile{x}"] = pygame.transform.scale(
            pygame.image.load(f"assets/floor/tile{tile_num}.png"), (16, 16)
        )

    for x in os.listdir("assets/character"):
        images[f"{x[:-4]}"] = pygame.image.load((f"assets/character/{x}"))
        images[f"{x[:-4]}_flipped"] = pygame.transform.flip(
            pygame.image.load((f"assets/character/{x}")), True, False
        )

    # load torch images

    for i in range(32):  # 31 frames total
        if i < 10:
            load_num = "0" + str(i)
        else:
            load_num = str(i)
        torch_img = pygame.image.load(f"assets/tools/torch/torch_{load_num}.png")

        cropped_surface = pygame.Surface(
            (torch_img.get_width() / 2, torch_img.get_height() / 2), pygame.SRCALPHA
        )
        cropped_surface.blit(
            torch_img,
            (-int(torch_img.get_width() / 4), -int(torch_img.get_height() / 2)),
        )
        cropped_surface = pygame.transform.scale(cropped_surface, (16, 16))
        images[f"torch{i}"] = cropped_surface

    return images


def create_world(map_w, map_h, chance_index):
    # add four to width and height to cut it out later, easier world generation with no edges
    map_w, map_h = map_w + 4, map_h + 4

    from perlin_noise import PerlinNoise

    noise = PerlinNoise(seed=random.randint(1, 1000000), octaves=10)

    world_gen = numpy.zeros((map_w, map_h))
    for x in range(map_w):
        for y in range(map_h):
            world_gen[y, x] = noise([x / map_w, y / map_h])

    world = numpy.zeros((map_h, map_w), dtype=int)
    plants = numpy.zeros((map_h, map_w), dtype=int)
    world_rotation = numpy.zeros((map_h, map_w), dtype=int)

    random_dict = {"plant": 10, "stone": 1, "flower": 7}
    choose_list = []
    for key in random_dict.keys():
        for _ in range(random_dict[key]):
            choose_list.append(str(key))

    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_gen[y, x] > 0:
                world[y, x] = random.choice([5, 6, 7])
                # plants[y, x] = 12
            else:
                world[y, x] = 14
                if random.randint(0, chance_index) == 1:
                    set_tile = random.choice(choose_list)

                    if set_tile == "plant":
                        plants[y, x] = random.choice(
                            [
                                123,
                                124,
                                125,
                                126,
                                11,
                                8,
                            ]
                        )

                    elif set_tile == "stone":
                        plants[y, x] = random.choice(
                            [
                                132,
                                133,
                                134,
                                135,
                                136,
                                137,
                            ]
                        )

                    elif set_tile == "flower":
                        plants[y, x] = random.choice(
                            [
                                110,
                                111,
                                112,
                                113,
                                127,
                            ]
                        )
                else:
                    pass
                    # plants[y, x] = 12

    world_copy = world
    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_copy[y, x] in [5, 6, 7]:
                # rand van wereld
                if not (
                    x == 0
                    or y == 0
                    or x == world.shape[1] - 1
                    or y == world.shape[1] - 1
                ):
                    grass_code = ""
                    grass_count = 0
                    for c in [
                        world_copy[y - 1, x],
                        world_copy[y, x + 1],
                        world_copy[y + 1, x],
                        world_copy[y, x - 1],
                    ]:
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
                # rand van wereld
                if (
                    x == 0
                    or y == 0
                    or x == world.shape[1] - 1
                    or y == world.shape[1] - 1
                ):
                    convert = True
                    check_code = "ssss"  # tijdelijk

                    # boven                  # rechts                  # onder              # links
                elif (
                    world_copy[y - 1, x] == 14
                    or world_copy[y, x + 1] == 14
                    or world_copy[y + 1, x] == 14
                    or world_copy[y, x - 1] == 14
                ):
                    convert = True
                    # check code: pos 0 = boven pos 1 = rechts pos 2 = onder, pos 3 = links
                    check_code = ""

                    for c in [
                        world_copy[y - 1, x],
                        world_copy[y, x + 1],
                        world_copy[y + 1, x],
                        world_copy[y, x - 1],
                    ]:
                        if c == 14:
                            check_code += "g"  # grass
                        else:  # 4,5,6
                            check_code += "s"  # sand
                if convert:  # volgorde: boven, rechts, onder, links
                    convert_dict = {
                        "sssg": 15,
                        "ssgs": 21,
                        "sgss": 23,
                        "gsss": 35,
                        "gssg": 16,
                        "ggss": 17,
                        "ssgg": 20,
                        "sggs": 19,
                    }
                    if check_code in convert_dict:
                        world[y, x] = convert_dict[check_code]

    world_copy_copy = world
    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_copy_copy[y, x] in [5, 6, 7]:
                # rand van wereld
                if not (
                    x == 0
                    or y == 0
                    or x == world.shape[1] - 1
                    or y == world.shape[1] - 1
                ):
                    generated_tiles = 0
                    gen_code = ""
                    for c in [
                        world_copy_copy[y - 1, x],
                        world_copy_copy[y, x + 1],
                        world_copy_copy[y + 1, x],
                        world_copy_copy[y, x - 1],
                    ]:
                        if c in [15, 21, 23, 35, 16, 17, 20, 19]:
                            generated_tiles += 1
                        if c in [5, 6, 7]:
                            gen_code += f"5-"
                        else:
                            gen_code += f"{c}-"

                    if generated_tiles == 2:  # boven, rechts, onder, links
                        gen_code = gen_code[:-1]
                        convert_dict = {
                            "17-35-5-5": 26,
                            "17-17-5-5": 26,
                            "23-17-5-5": 26,
                            "23-35-5-5": 26,
                            "15-5-5-35": 28,
                            "15-5-5-16": 28,
                            "16-5-5-35": 28,
                            "16-5-5-16": 28,
                            "5-21-19-5": 25,
                            "5-19-23-5": 25,
                            "5-19-19-5": 25,
                            "5-21-23-5": 25,
                            "5-5-15-20": 34,
                            "5-5-20-21": 34,
                            "5-5-15-21": 34,
                            "5-5-20-20": 34,
                        }

                        if gen_code in convert_dict:
                            world[y, x] = convert_dict[gen_code]

    with open("convert_tiles.json") as f:
        convert_dict = json.load(f)

    world_copy_copy = world
    for x in range(world.shape[1]):
        for y in range(world.shape[0]):
            if world_copy_copy[y, x] in [5, 6, 7]:
                # rand van wereld
                if not (
                    x == 0
                    or y == 0
                    or x == world.shape[1] - 1
                    or y == world.shape[1] - 1
                ):
                    generated_tiles = 0
                    gen_code = ""
                    for c in [
                        world_copy_copy[y - 1, x],
                        world_copy_copy[y, x + 1],
                        world_copy_copy[y + 1, x],
                        world_copy_copy[y, x - 1],
                    ]:
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
                if world[sec_y, sec_x] not in [14] or plants[sec_y, sec_x] in [
                    48,
                    49,
                    61,
                    62,
                ]:
                    spawn_tree = False

        if spawn_tree:
            plants[y, x] = 48
            plants[y, x + 1] = 49
            plants[y + 1, x] = 61
            plants[y + 1, x + 1] = 62

    world = world[2 : map_w - 2, 2 : map_h - 2]
    plants = plants[2 : map_w - 2, 2 : map_h - 2]
    return plants, world, world_rotation


def render_world(
    screen,
    world,
    plants,
    world_rotation,
    images,
    scrollx,
    scrolly,
    screenW,
    screenH,
    torch_animation_frame,
    torch_update_frame,
):
    world_h, world_w = world.shape
    tile_size = 16

    draw_x_from = int(scrollx / tile_size)
    draw_x_to = int((scrollx + screenW) / tile_size) + 1

    draw_y_from = int(scrolly / tile_size)
    draw_y_to = int((scrolly + screenH) / tile_size) + 1

    if time.perf_counter() - torch_update_frame > 0.0825:
        torch_update_frame = time.perf_counter()
        torch_animation_frame = (torch_animation_frame + 1) % 31

    draw_radius = 170 - math.sin(time.perf_counter() * 2) * 10
    draw_radius_bright = 100 - math.sin(time.perf_counter() * 2) * 5

    add_surf = pygame.Surface((400, 400), pygame.SRCALPHA)
    add_surf_bright = pygame.Surface((400, 400), pygame.SRCALPHA)
    add_value = 75

    pygame.draw.circle(
        add_surf,
        (add_value, add_value, int(add_value / 1.8)),
        (200, 200),
        draw_radius,
    )
    pygame.draw.circle(
        add_surf_bright,
        (add_value - 10, add_value - 10, int(add_value / 1.8) - 10),
        (200, 200),
        draw_radius_bright,
    )

    for x in range(draw_x_from, min(draw_x_to, world_w)):
        for y in range(draw_y_from, min(draw_y_to, world_h)):
            screen.blit(
                images[f"tile{world[y, x]}"],
                (x * tile_size - scrollx, y * tile_size - scrolly),
            )

            if plants[y, x] != 0:
                if plants[y, x] != 138:
                    screen.blit(
                        images[f"tile{plants[y, x]}"],
                        (x * tile_size - scrollx, y * tile_size - scrolly),
                    )
                else:
                    screen.blit(
                        images[f"torch{torch_animation_frame}"],
                        (x * tile_size - scrollx, y * tile_size - scrolly),
                    )

    return torch_animation_frame, torch_update_frame


def render_plants(
    screen,
    world,
    plants,
    world_rotation,
    images,
    scrollx,
    scrolly,
    screenW,
    screenH,
    player,
):
    world_h, world_w = world.shape
    tile_size = 16

    draw_x_from = int(scrollx / tile_size)
    draw_x_to = int((scrollx + screenW) / tile_size) + 1

    draw_y_from = int(scrolly / tile_size)
    draw_y_to = int((scrolly + screenH) / tile_size) + 1

    draw_x_from += 10
    draw_y_from += 10
    draw_x_to -= 10
    draw_y_to -= 10

    for x in range(draw_x_from, min(draw_x_to, world_w)):
        for y in range(draw_y_from, min(draw_y_to, world_h)):
            # screen.blit(images[f"tile{world[y, x]}"], (x * tile_size - scrollx, y * tile_size - scrolly))
            if plants[y, x] != 0:
                # exception for tree tiles 48, 49, (not for bottom: 61, 62)
                if plants[y, x] in [48, 49]:
                    if player.y + 16 + 4 - 16 < y * tile_size:
                        screen.blit(
                            images[f"tile{plants[y, x]}"],
                            (x * tile_size - scrollx, y * tile_size - scrolly),
                        )
                if player.y + 16 + 4 < y * tile_size:
                    if plants[y, x] != 138:
                        screen.blit(
                            images[f"tile{plants[y, x]}"],
                            (x * tile_size - scrollx, y * tile_size - scrolly),
                        )


def render_torch(
    screen,
    world,
    plants,
    world_rotation,
    images,
    screenW,
    screenH,
    scrollx,
    scrolly,
):
    world_h, world_w = world.shape

    tile_size = 16
    draw_x_from = int(scrollx / tile_size)
    draw_x_to = int((scrollx + screenW) / tile_size) + 1

    draw_y_from = int(scrolly / tile_size)
    draw_y_to = int((scrolly + screenH) / tile_size) + 1

    add_surf = pygame.Surface((400, 400), pygame.SRCALPHA)
    add_surf_bright = pygame.Surface((400, 400), pygame.SRCALPHA)
    add_value = 50

    draw_radius = 130 - math.cos(time.perf_counter() * 2) * 10
    draw_radius_bright = 80 - math.cos(time.perf_counter() * 2) * 5
    pygame.draw.circle(
        add_surf, (add_value, add_value, int(add_value / 2.5)), (200, 200), draw_radius
    )
    pygame.draw.circle(
        add_surf_bright,
        (add_value - 10, add_value - 10, int(add_value / 2.5) - 10),
        (200, 200),
        draw_radius_bright,
    )

    torch_locations_list = []

    for x in range(draw_x_from, min(draw_x_to, world_w)):
        for y in range(draw_y_from, min(draw_y_to, world_h)):
            if plants[y, x] == 138:
                screen.blit(
                    add_surf,
                    (
                        x * tile_size - scrollx - int(add_surf.get_width() / 2) + 8,
                        y * tile_size - scrolly - int(add_surf.get_height() / 2) + 8,
                    ),
                    special_flags=pygame.BLEND_RGB_ADD,
                )

                screen.blit(
                    add_surf_bright,
                    (
                        x * tile_size
                        - scrollx
                        - int(add_surf_bright.get_width() / 2)
                        + 8,
                        y * tile_size
                        - scrolly
                        - int(add_surf_bright.get_height() / 2)
                        + 8,
                    ),
                    special_flags=pygame.BLEND_RGB_ADD,
                )

                torch_locations_list.append([x, y])

    return torch_locations_list


def render_lantern(
    screen,
    world,
    plants,
    world_rotation,
    images,
    scrollx,
    scrolly,
    screenW,
    screenH,
    player,
):
    world_h, world_w = world.shape
    tile_size = 16

    grid_y, grid_x = player.player_tile[1] + 1, player.player_tile[0] + 1

    # print(grid_x, grid_y)

    draw_x_from, draw_x_to = grid_x, grid_x
    draw_y_from, draw_y_to = grid_y, grid_y

    draw_x_from -= 10
    draw_y_from -= 10
    draw_x_to += 10
    draw_y_to += 10

    add_surf = pygame.Surface((400, 400), pygame.SRCALPHA)
    add_surf_bright = pygame.Surface((400, 400), pygame.SRCALPHA)
    add_value = 75

    draw_radius = 170 - math.sin(time.perf_counter() * 2) * 10
    draw_radius_bright = 100 - math.sin(time.perf_counter() * 2) * 5
    pygame.draw.circle(
        add_surf, (add_value, add_value, int(add_value / 1.8)), (200, 200), draw_radius
    )
    pygame.draw.circle(
        add_surf_bright,
        (add_value - 10, add_value - 10, int(add_value / 1.8) - 10),
        (200, 200),
        draw_radius_bright,
    )

    # pygame.draw.rect(
    #     add_surf,
    #     (add_value, add_value, int(add_value / 1.8)),
    #     ((0, 0), (400, 400)),
    #     border_radius=10,
    # )
    # add_surf.set_alpha(15)

    screen.blit(
        add_surf,
        (
            player.x + 24 - int(add_surf.get_width() / 2) - scrollx,
            player.y + 24 - int(add_surf.get_height() / 2) - scrolly,
        ),
        special_flags=pygame.BLEND_RGB_ADD,
    )

    screen.blit(
        add_surf_bright,
        (
            player.x + 24 - int(add_surf_bright.get_width() / 2) - scrollx,
            player.y + 24 - int(add_surf_bright.get_height() / 2) - scrolly,
        ),
        special_flags=pygame.BLEND_RGB_ADD,
    )

    # for x in range(draw_x_from, min(draw_x_to, world_w)):
    #     for y in range(draw_y_from, min(draw_y_to, world_h)):
    #         screen.blit(
    #             add_surf,
    #             (x * tile_size - scrollx, y * tile_size - scrolly),
    #             special_flags=pygame.BLEND_RGB_ADD,
    #         )

    # screen.blit(
    #         images[f"tile{world[y, x]}"],
    #         (x * tile_size - scrollx, y * tile_size - scrolly),
    #     )
    # if plants[y, x] != 0:
    #     screen.blit(
    #         images[f"tile{plants[y, x]}"],
    #         (x * tile_size - scrollx, y * tile_size - scrolly),
    #     )


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
