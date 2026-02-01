import math

import pygame
import numpy
import random
import os
import time
import json
from scripts.particle import *

# from scripts.ui import *

pygame.mixer.init()

with open("controller_type.txt") as f:
    controller_type = f.read()

joystick_btn_dict = {}
if controller_type != "":
    with open("joystick_btn_dict.json") as f:
        joystick_btn_dict = json.load(f)
        joystick_btn_dict = joystick_btn_dict[controller_type]
        print(joystick_btn_dict)


def render_text(text, pos, color, font, screen):
    text_render = font.render(str(text), True, color)
    screen.blit(text_render, pos)


def render_text_with_outline(text, pos, colorBG, colorFG, font, screen):
    render_text(text, (pos[0] + 1, pos[1] - 1), colorBG, font, screen)
    render_text(text, (pos[0] + 1, pos[1] + 1), colorBG, font, screen)
    render_text(text, (pos[0] - 1, pos[1] - 1), colorBG, font, screen)
    render_text(text, (pos[0] - 1, pos[1] + 1), colorBG, font, screen)

    render_text(text, (pos[0], pos[1]), colorFG, font, screen)


def get_distance(x1, y1, x2, y2):
    c2 = math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2)
    c = math.sqrt(c2)
    return c


def load_img():
    images = {}

    for x in range(141):
        if x not in [138]:
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


def create_world(map_w, map_h, chance_index, seed=random.randint(1, 1000000)):
    # add four to width and height to cut it out later, easier world generation with no edges
    map_w, map_h = map_w + 4, map_h + 4

    from perlin_noise import PerlinNoise

    noise = PerlinNoise(seed=seed, octaves=10)

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
    world_rotation = world_rotation[2 : map_w - 2, 2 : map_h - 2]
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
