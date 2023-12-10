# BUGS:
# 1. Inventory switching item in Crafting table

import numpy
import random

import pygame
import time
import json

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
maxFps = 60

fps_font = pygame.font.Font("assets/Font/Main.ttf", 15)

screenWidth = 1000
screenHeight = 600

joystick = None
joystick_input = None
controller_type = None
joystick_btn_dict = None

check_controller_perf = -1


def get_joysticks():
    global joystick, joystick_input, controller_type, joystick_btn_dict
    if pygame.joystick.get_count() == 1:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        # print("Joystick found!!!")
    else:
        joystick = None
        joystick_input = False
        # print("No joystick connected")

    if joystick:
        controller_type = joystick.get_name()
    else:
        controller_type = None

    if controller_type in ["PS4 Controller", "Xbox 360 Controller"]:
        with open("joystick_btn_dict.json") as f:
            joystick_btn_dict = json.load(f)
            joystick_btn_dict = joystick_btn_dict[controller_type]

        with open("controller_type.txt", "w") as f:
            f.write(str(controller_type))
    else:
        with open("controller_type.txt", "w") as f:
            f.write(str(""))

    return joystick, joystick_input, controller_type, joystick_btn_dict


joystick, joystick_input, controller_type, joystick_btn_dict = get_joysticks()

from func import *
from scripts.enemies import *
from scripts.particle import *
from scripts.player import *
from scripts.ui import *
from scripts.animal import *


# joystick_btn_dict = {
#     "Xbox 360 Controller": {
#         "south-btn": "joystick.get_button(0)",
#         "east-btn": "joystick.get_button(1)",
#         "west-btn": "joystick.get_button(2)",
#         "north-btn": "joystick.get_button(3)",

#         "crafting_table": "joystick.get_button(7)",  # START btn

#         "d-pad-up": "joystick.get_hat(0)[1] > 0",
#         "d-pad-down": "joystick.get_hat(0)[1] < 0",
#         "d-pad-right": "joystick.get_hat(0)[0] > 0",
#         "d-pad-left": "joystick.get_hat(0)[0] < 0",
#     },
#     "PS4 Controller": {
#         "south-btn": "joystick.get_button(0)",
#         "east-btn": "joystick.get_button(1)",
#         "west-btn": "joystick.get_button(2)",
#         "north-btn": "joystick.get_button(3)",

#         "crafting_table": "joystick.get_button(6)",  # OPTIONS btn

#         "d-pad-up": "joystick.get_button(11)",
#         "d-pad-down": "joystick.get_button(12)",
#         "d-pad-left": "joystick.get_button(13)",
#         "d-pad-right": "joystick.get_button(14)"
#     }
# }


screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
pygame.display.set_caption("Hambala")
icon = pygame.image.load("assets/character/idle1.png").convert_alpha()
icon = pygame.transform.scale(icon, (60, 60))
pygame.display.set_icon(icon)
screenWidth = screen.get_width()
screenHeight = screen.get_height()
playing = True
plant_spawn_chance = 3

stamina_icon = pygame.image.load("assets/icons/stamina.png").convert_alpha()
hunger_icon = pygame.image.load("assets/icons/hunger_icon.png").convert_alpha()
health_icon = pygame.image.load("assets/icons/health_icon.png").convert_alpha()

mask_surf = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA, 32)
sky_color = (0, 0, 0, 150)
mask_surf.fill(sky_color)
is_night = False
sky_time = 0
light = pygame.image.load("assets/Images/Light.png").convert_alpha()

scrollx = 0
scrolly = 0

map_w, map_h = 150, 150

plants, world, world_rotation = create_world(map_w, map_h, plant_spawn_chance)

player_sprint_bar = ValueBar((screenWidth - 208, screenHeight - 33), (200, 25), 8, 100)

player_hunger_bar = ValueBar(
    (screenWidth - 208, screenHeight - 66 - 8), (200, 25), 8, 10000
)

torch_locations_list = []

player_hp_bar = ValueBar(
    (screenWidth / 2 - screenWidth / 8, screenHeight - 33), (screenWidth / 4, 25), 8, 10
)

main_inventory = Inventory((50, 400), (8, screenHeight / 2 - 200))
main_crafting_table = CraftingTable()
main_crafting_table.set_inventory(main_inventory)
main_inventory.set_crafting_table(main_crafting_table)
animals = Animal(random.randint(25, 45), screenWidth, screenHeight)
animals.set_inventory(main_inventory)

torch_update_frame = -1
torch_animation_frame = 0


enemies = Enemies(
    {"zombie": random.randint(20, 100)},
    {"zombie": random.randint(50, 60)},
    {"zombie": random.randint(20, 30)},
)
enemies_spawn = False

images = load_img()

particles = []

keys = pygame.key.get_pressed()
player = Player(
    images, ((map_w * 16) - 48) / 2, ((map_h * 16) - 48) / 2, controller_type
)
particle_perf = -1
player.get_inventory(main_inventory)
main_inventory.get_player(player)

animals.player = player

deltaT = 0

prev_player_x = 0
prev_player_y = 0

scrollx = ((map_w * 16) - screenWidth) / 2
scrolly = ((map_h * 16) - screenHeight) / 2

shake_x = 0
shake_y = 0
shake_frame = 0

mouse_set_x = 300
mouse_set_y = 300

cursor = pygame.image.load("assets/icons/cursor.png").convert_alpha()
pygame.mouse.set_visible(False)
cursor_rect = cursor.get_rect()

shake_time = time.perf_counter()
started_shake = False


def shake(shakeTime, scrollx, scrolly):
    global started_shake
    if time.perf_counter() - shake_time < shakeTime:
        scrollx += random.randint(-2, 2)
        scrolly += random.randint(-2, 2)
    else:
        started_shake = False


while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False

        if (
            event.type == pygame.MOUSEWHEEL
            or event.type == pygame.JOYBUTTONDOWN
            or event.type == pygame.JOYHATMOTION
        ):
            if not joystick_input and hasattr(event, "y"):
                main_inventory.mouse_update(
                    event.y, joystick_input, joystick, joystick_btn_dict
                )
            else:
                main_inventory.mouse_update(
                    0, joystick_input, joystick, joystick_btn_dict
                )

        if joystick:
            if event.type == pygame.JOYBUTTONDOWN:
                joystick_input = True

        if (
            event.type == pygame.KEYDOWN
            or event.type == pygame.JOYBUTTONDOWN
            or event.type == pygame.JOYHATMOTION
        ):
            if hasattr(event, "key"):
                if event.key in [pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s]:
                    joystick_input = False
            if joystick_input:
                if eval(joystick_btn_dict["d-pad-right"]):
                    main_inventory.backpack_visible = True
                elif eval(joystick_btn_dict["d-pad-left"]):
                    main_inventory.backpack_visible = False
            else:
                if hasattr(event, "key"):
                    if event.key == pygame.K_CAPSLOCK:
                        main_inventory.backpack_visible = (
                            not main_inventory.backpack_visible
                        )

        if event.type == pygame.VIDEORESIZE:
            screenWidth, screenHeight = screen.get_size()
            player_sprint_bar.reset(
                (screenWidth - 208, screenHeight - 33), (200, 25), 8
            )
            player_hunger_bar.reset(
                (screenWidth - 208, screenHeight - 66 - 8), (200, 25), 8
            )
            player_hp_bar.reset(
                (screenWidth / 2 - screenWidth / 8, screenHeight - 33),
                (screenWidth / 4, 25),
                8,
            )
            player.set_window_size(screen)
            main_inventory.reset_pos((8, screenHeight / 2 - 200))
            main_crafting_table.reset()
            animals.reset_screen_size(screenWidth, screenHeight)
            mask_surf = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA, 32)
            mask_surf.fill(sky_color)

    screen.fill((0, 0, 0))
    torch_animation_frame, torch_update_frame = render_world(
        screen,
        world,
        plants,
        world_rotation,
        images,
        scrollx + shake_x,
        scrolly + shake_y,
        screenWidth,
        screenHeight,
        torch_animation_frame,
        torch_update_frame,
    )
    animals.draw(screen, scrollx + shake_x, scrolly + shake_y)
    enemies.draw_enemies(screen, scrollx + shake_x, scrolly + shake_y)
    particles = animals.update(plants, player, particles)

    prev_player_x = player.x
    prev_player_y = player.y
    player.draw(screen, scrollx, scrolly)

    # get joystick

    if time.perf_counter() - check_controller_perf > 1.5:
        joystick, joystick_input, controller_type, joystick_btn_dict = get_joysticks()
        check_controller_perf = time.perf_counter()

    render_plants(
        screen,
        world,
        plants,
        world_rotation,
        images,
        scrollx + shake_x,
        scrolly + shake_y,
        screenWidth,
        screenHeight,
        player,
    )

    if animals.hit:
        # if not started_shake:
        #     shake_time = time.perf_counter()
        #     started_shake = True
        # shake(shake_time, scrollx, scrolly)
        shake_frame = 1
        animals.hit = False

    if shake_frame > 0:
        shake_frame += 1
        if shake_frame > 10:
            shake_frame = 0
        shake_x = random.randint(-1, 1)
        shake_y = random.randint(-1, 1)

    particles, particle_perf = spawn_particles(particle_perf, player, particles)

    del_list = []
    for i, particle in enumerate(particles):
        particle.update(scrollx + shake_x, scrolly + shake_y, deltaT, player, world)
        particle.draw(screen)
        if particle.delete_timer + 0.75 < time.perf_counter():
            del_list.append(i)

    for j in list(sorted(del_list))[::-1]:
        particles.pop(j)

    screen.blit(mask_surf, (0, 0))

    player_sprint_bar.draw(
        screen,
        pygame.Color("#212529"),
        pygame.Color("#343a40"),
        pygame.Color("#F4D35E"),
        stamina_icon,
        (-25, 0),
        5,
    )

    player_hunger_bar.draw(
        screen,
        pygame.Color("#212529"),
        pygame.Color("#343a40"),
        pygame.Color("#bc6c25"),
        hunger_icon,
        (-25, 0),
        5,
    )

    player_hp_bar.draw(
        screen,
        pygame.Color("#212529"),
        pygame.Color("#343a40"),
        player.hp_bar_color,
        player.hp_icon,
        (-28, -2),
        5,
    )

    player_sprint_bar.update(player.energy_value)
    player_hunger_bar.update(player.food_value)
    player_hp_bar.update(player.health_value)
    keys = pygame.key.get_pressed()

    main_inventory.draw(screen, pygame.mouse.get_pos(), scrollx, scrolly)

    player.walking(
        keys,
        deltaT,
        pygame.mouse.get_pressed(),
        joystick,
        joystick_input,
        joystick_btn_dict,
        plants,
    )
    player.update(
        plants, keys, screen, joystick, joystick_input, player_hp_bar, joystick_btn_dict
    )

    particles = enemies.update(enemies_spawn, player, torch_locations_list, particles)

    main_inventory.draw_holding_items(screen, (scrollx, scrolly))

    if time.perf_counter() - sky_time > 0.8:
        if not is_night:
            sky_color = (sky_color[0], sky_color[1], sky_color[2], sky_color[3] + 0.25)
        else:
            sky_color = (sky_color[0], sky_color[1], sky_color[2], sky_color[3] - 0.25)

        sky_time = time.perf_counter()

    mask_surf.fill(sky_color)

    if player.holding_lantern:
        render_lantern(
            screen,
            world,
            plants,
            world_rotation,
            images,
            scrollx + shake_x,
            scrolly + shake_y,
            screenWidth,
            screenHeight,
            player,
        )

    torch_locations_list = render_torch(
        screen,
        world,
        plants,
        world_rotation,
        images,
        screenWidth,
        screenHeight,
        scrollx,
        scrolly,
    )

    if sky_color[3] > 125:
        enemies_spawn = True
    else:
        enemies_spawn = False

    if sky_color[3] > 200:
        is_night = True
    elif sky_color[3] < 1:
        is_night = False

    scrollx += int((player.x - int((screenWidth - 48) / 2) - scrollx) / 5)
    scrolly += int((player.y - int((screenHeight - 48) / 2) - scrolly) / 5)

    scrollx = max(scrollx, 0)
    scrollx = min(scrollx, 16 * map_w - screenWidth)
    scrolly = max(scrolly, 0)
    scrolly = min(scrolly, 16 * map_h - screenHeight)

    main_inventory.update(
        pygame.mouse.get_pressed(),
        pygame.mouse.get_pos(),
        screen,
        pygame.key.get_pressed(),
        joystick_input,
        joystick,
        (scrollx, scrolly),
        plants,
        main_inventory,
        joystick_btn_dict,
    )

    main_crafting_table.draw(
        screen,
        scrollx,
        scrolly,
        pygame.key.get_pressed(),
        joystick_input,
        joystick,
        plants,
        main_inventory,
        joystick_btn_dict,
    )
    main_crafting_table.update(
        keys,
        pygame.mouse.get_pos(),
        pygame.mouse.get_pressed(),
        joystick_input,
        joystick,
        (scrollx, scrolly),
        joystick_btn_dict,
    )

    cursor_rect.topleft = pygame.mouse.get_pos()
    if (
        not main_inventory.holding_item
        and not main_crafting_table.holding_item
        and not main_inventory.can_place_item
    ):
        screen.blit(cursor, cursor_rect)

    if joystick_input:
        axis_x_2, axis_y_2 = joystick.get_axis(2), joystick.get_axis(3)
        if abs(axis_x_2) > 0.15:
            mouse_set_x += joystick.get_axis(2) * deltaT
        if abs(axis_y_2) > 0.15:
            mouse_set_y += joystick.get_axis(3) * deltaT

        mouse_set_x = min(max(5, mouse_set_x), screenWidth - 5)
        mouse_set_y = min(max(5, mouse_set_y), screenHeight - 5)
        pygame.mouse.set_pos((mouse_set_x, mouse_set_y))

    fps = clock.get_fps()
    screen.blit(fps_font.render(str(int(fps)), True, (0, 0, 0)), (10, 10))
    pygame.display.update()
    deltaT = clock.tick(60)
    if joystick_input:
        if eval(joystick_btn_dict["d-pad-right"]):
            print("RIGHT")

pygame.quit()
