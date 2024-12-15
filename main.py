#                    TODO
# ---------------------------------------------
# ! Bugfixen resize settings scherm :))) [✘]  <--- 'NEEE' - Tamer Sparreboom 8-12-2024
# ! Create game settings (seed, difficulty). [✘]
# ! FPS Counter setting. [✘]
# --------------------------------------------
# * Pause screen resize fixen. [✓]
# * Play last saved. [✓]
# * Screens resize fixen. [✓]
# * Inventory laad bug fixen. [✓]
# * Saves verwijderen. [✓]
# * Search functie load world werkend maken. [✓]
# * Create game met zelfde naam ERROR!!. [✓]
# * Instellingen (algemeen) maken. [✓]
# --------------------------------------------

import numpy
import random

import pygame
import time
import json
import pygame_gui
import math

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
from scripts.bow import *

from scripts.windows.title_window import *
from scripts.windows.create_game_window import *
from scripts.windows.load_save_window import *
from scripts.windows.pause_menu_window import *
from scripts.windows.main_settings_window import *

import json
import os
import copy

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

pause_menu_opened = False

stamina_icon = pygame.image.load("assets/icons/stamina.png").convert_alpha()
hunger_icon = pygame.image.load("assets/icons/hunger_icon.png").convert_alpha()
health_icon = pygame.image.load("assets/icons/health_icon.png").convert_alpha()

mask_surf = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA, 32)
sky_color = [0, 0, 0, 0]
mask_surf.fill(sky_color)
is_night = False
night_count = 0
sky_time = 0
light = pygame.image.load("assets/Images/Light.png").convert_alpha()
game_size_set = False

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
    {
        "zombie": (10, 20),
        "zombie-big": (40, 60),
        "slime-green": (5, 10),
        "slime-red": (10, 25),
        "slime-blue": (2, 4),
        "slime-white": (20, 40),
    },
    {
        "zombie": (20, 30),
        "zombie-big": (5, 10),
        "slime-green": (5, 10),
        "slime-red": (15, 20),
        "slime-blue": (25, 35),
        "slime-white": (4, 8),
    },
    {
        "zombie": (70, 120),
        "zombie-big": (150, 200),
        "slime-green": (20, 40),
        "slime-red": (20, 40),
        "slime-blue": (10, 20),
        "slime-white": (80, 150),
    },
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
dt = 1 # deltaT value / 16

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

shake_time = 3
started_shake = False

ui_clock = Clock((10, 10), (80, 80), (0, 0, 0, 0), False)

player_bow = Bow(unlimited_arrows=True)

current_game_state = "TITLE"
"""
TITLE = Title screen (when opening game):

Buttons in title screen:
Load last game -> GAME (met ingeladen spel)
Load (specific) game -> LOAD
Create new game -> CREATE
Settings -> SETTINGS
Exit -> pg.quit() etc.

LOAD = Load specific game:
Play -> GAME

CREATE = Create screen game

SETTINGS = General game settings

GAME = In-Game
PAUSE = Pause screen (when opening menu in game)
"""

in_game = False  # je kan ook in-game zijn in settings

loaded_world = "testsave"


def shake(shakeTime, scrollx, scrolly):
    global started_shake
    if time.perf_counter() > shakeTime + 0.5:
        started_shake = False
    else:
        scrollx += random.randint(-2, 2)
        scrolly += random.randint(-2, 2)


title_window = TitleWindow(screen)
create_game_window = CreateGameWindow(screen)
load_save_window = LoadSaveWindow(screen)
pause_menu_window = PauseMenuWindow(screen)
settings_window = MainSettingsWindow(screen)

black_surface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
black_surface.fill((0, 0, 0))
black_surface.set_alpha(100)


def save_world():
    json_dict = {}
    with open(os.path.join("saves", str(loaded_world), "save.json"), "r") as f:
        json_dict = json.loads(f.read())

    with open(os.path.join("saves", str(loaded_world), "save.json"), "w") as f:
        dict_copy = copy.copy(json_dict)

        dict_copy["time"] = sky_color[3]

        dict_copy["animal_dict"] = animals.return_animal_dict()
        dict_copy["alive_enemies"] = enemies.return_enemies_list()

        dict_copy["player"]["x"] = player.x
        dict_copy["player"]["y"] = player.y
        dict_copy["player"]["energy_value"] = player.energy_value
        dict_copy["player"]["food_value"] = player.food_value
        dict_copy["player"]["health_value"] = player.health_value

        dict_copy["inventory"]["block_fill"] = main_inventory.block_fill
        dict_copy["inventory"]["item_count_dict"] = main_inventory.item_count_dict

        f.write(json.dumps(dict_copy))  #! boos

    # WORLD
    with open(os.path.join("saves", str(loaded_world), "world.txt"), "w") as f:
        numpy.savetxt(f, world.astype(int), fmt="%i")

    with open(os.path.join("saves", str(loaded_world), "world_rotation.txt"), "w") as f:
        numpy.savetxt(f, world_rotation.astype(int), fmt="%i")

    with open(os.path.join("saves", str(loaded_world), "plants.txt"), "w") as f:
        numpy.savetxt(f, plants.astype(int), fmt="%i")

    print("WERELD OPGESLAGEN!!!")


def load_world(folder_name, sky_color):
    print("FOLDER NAME", folder_name)
    with open(os.path.join("saves", str(folder_name), "save.json")) as f:
        json_dict = json.loads(f.read())

    dict_copy = copy.copy(json_dict)

    sky_clr = [sky_color[0], sky_color[1], sky_color[2], dict_copy["time"]]

    animals.convert_animal_json_dict(dict_copy["animal_dict"])

    enemies.convert_enemies_json(dict_copy["alive_enemies"])

    player.x = dict_copy["player"]["x"]
    player.y = dict_copy["player"]["y"]
    player.energy_value = dict_copy["player"]["energy_value"]
    player.food_value = dict_copy["player"]["food_value"]
    player.health_value = dict_copy["player"]["health_value"]

    block_fill_copy = {}
    for key in dict_copy["inventory"]["block_fill"].keys():
        block_fill_copy[int(key)] = dict_copy["inventory"]["block_fill"][key]

    main_inventory.block_fill = block_fill_copy

    item_count_copy = {}
    for key in dict_copy["inventory"]["item_count_dict"].keys():
        item_count_copy[int(key)] = dict_copy["inventory"]["item_count_dict"][key]

    main_inventory.item_count_dict = item_count_copy

    print(
        "FOLDER NAME", folder_name, os.path.join("saves", str(folder_name), "world.txt")
    )
    world = numpy.loadtxt(os.path.join("saves", str(folder_name), "world.txt")).reshape(
        map_w, map_h
    )
    world = world.astype(int)

    world_rotation = numpy.loadtxt(
        os.path.join("saves", str(folder_name), "world_rotation.txt")
    ).reshape(map_w, map_h)
    world_rotation = world_rotation.astype(int)

    plants = numpy.loadtxt(
        os.path.join("saves", str(folder_name), "plants.txt")
    ).reshape(map_w, map_h)
    plants = plants.astype(int)

    return sky_clr, world, world_rotation, plants


while playing:
    if current_game_state == "TITLE":
        scrollx = 0
        scrolly = 0

        screen.fill((0, 0, 0))
        events = pygame.event.get()
        playing, current_game_state, loaded_world = title_window.update(
            events,
            pygame.mouse.get_pos()[0],
            pygame.mouse.get_pos()[1],
            pygame.mouse.get_pressed()[0],
            deltaT,
        )

        if current_game_state != "TITLE":
            create_game_window.update_res(screen)
            load_save_window.update_res(screen)

        for event in events:
            if event.type == pygame.VIDEORESIZE:
                screenWidth, screenHeight = screen.get_size()
                animals.reset_screen_size(screenWidth, screenHeight)

                black_surface = pygame.Surface(
                    (screenWidth, screenHeight), pygame.SRCALPHA
                )
                black_surface.fill((0, 0, 0))
                black_surface.set_alpha(100)

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

        particles = animals.update(plants, player, particles, dt)

        screen.blit(black_surface, (0, 0))

        title_window.draw()

    elif current_game_state == "LOAD":
        scrollx = 0
        scrolly = 0
        screen.fill((0, 0, 0))
        events = pygame.event.get()
        playing, current_game_state, selected_world = load_save_window.update(
            events,
            pygame.mouse.get_pos()[0],
            pygame.mouse.get_pos()[1],
            pygame.mouse.get_pressed()[0],
            deltaT,
        )

        if current_game_state != "LOAD":
            title_window.update_res(screen)

        if selected_world != "":
            # wereld laad basis gangsters
            loaded_world = selected_world  # zodat de wereld ook opgeslagen kan worden
            sky_color, world, world_rotation, plants = load_world(
                selected_world, sky_color
            )

        for event in events:
            if event.type == pygame.VIDEORESIZE:
                screenWidth, screenHeight = screen.get_size()
                animals.reset_screen_size(screenWidth, screenHeight)

                black_surface = pygame.Surface(
                    (screenWidth, screenHeight), pygame.SRCALPHA
                )
                black_surface.fill((0, 0, 0))
                black_surface.set_alpha(100)

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

        particles = animals.update(plants, player, particles, dt)

        screen.blit(black_surface, (0, 0))

        load_save_window.draw()

    elif current_game_state == "CREATE":
        scrollx = 0
        scrolly = 0
        screen.fill((0, 0, 0))
        events = pygame.event.get()
        playing, current_game_state, loaded_world = create_game_window.update(
            events,
            pygame.mouse.get_pos()[0],
            pygame.mouse.get_pos()[1],
            pygame.mouse.get_pressed()[0],
            loaded_world,
            deltaT,
        )
        if current_game_state != "CREATE":
            title_window.update_res(screen)

        for event in events:
            if event.type == pygame.VIDEORESIZE:
                screenWidth, screenHeight = screen.get_size()
                animals.reset_screen_size(screenWidth, screenHeight)

                black_surface = pygame.Surface(
                    (screenWidth, screenHeight), pygame.SRCALPHA
                )
                black_surface.fill((0, 0, 0))
                black_surface.set_alpha(100)

        if current_game_state == "GAME":

            sky_color, world, world_rotation, plants = load_world(
                loaded_world, sky_color
            )

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

        particles = animals.update(plants, player, particles, dt)

        screen.blit(black_surface, (0, 0))

        create_game_window.draw()

    elif current_game_state == "SETTINGS":
        scrollx = 0
        scrolly = 0
        screen.fill((0, 0, 0))
        events = pygame.event.get()
        playing, current_game_state, loaded_world = settings_window.update(
            events,
            pygame.mouse.get_pos()[0],
            pygame.mouse.get_pos()[1],
            pygame.mouse.get_pressed()[0],
            deltaT,
        )
        if current_game_state != "SETTINGS":
            title_window.update_res(screen)

        for event in events:
            if event.type == pygame.VIDEORESIZE:
                screenWidth, screenHeight = screen.get_size()
                animals.reset_screen_size(screenWidth, screenHeight)

                black_surface = pygame.Surface(
                    (screenWidth, screenHeight), pygame.SRCALPHA
                )
                black_surface.fill((0, 0, 0))
                black_surface.set_alpha(100)

        if current_game_state == "GAME":
            sky_color, world, world_rotation, plants = load_world(
                loaded_world, sky_color
            )

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

        particles = animals.update(plants, player, particles, dt)

        screen.blit(black_surface, (0, 0))

        settings_window.draw()

    elif current_game_state == "PAUSE":
        pass

    elif current_game_state == "GAME":
        # peter pan
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                playing = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_4:
                    print("saving world...")
                    save_world()

                if event.key == pygame.K_ESCAPE:
                    pause_menu_window.update_res(screen)
                    pause_menu_opened = not pause_menu_opened

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    player_bow.start_charge()

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_LEFT:
                    player_bow.shoot_arrow()

            if (
                event.type == pygame.MOUSEWHEEL
                or event.type == pygame.JOYBUTTONDOWN
                or event.type == pygame.JOYHATMOTION
            ):
                if not pause_menu_opened:
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
                        if not pause_menu_opened:
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
                mask_surf = pygame.Surface(
                    (screenWidth, screenHeight), pygame.SRCALPHA, 32
                )
                mask_surf.fill(sky_color)

                black_surface.fill((0, 0, 0))
                black_surface.set_alpha(100)

        if not game_size_set:
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

            black_surface.fill((0, 0, 0))
            black_surface.set_alpha(100)

            game_size_set = True

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
        if not pause_menu_opened:
            particles = animals.update(plants, player, particles, dt)

        prev_player_x = player.x
        prev_player_y = player.y
        player.draw(screen, scrollx, scrolly, player_bow)

        # get joystick

        if time.perf_counter() - check_controller_perf > 1.5:
            joystick, joystick_input, controller_type, joystick_btn_dict = (
                get_joysticks()
            )
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

        if shake_frame > 0:
            shake_frame += 1
            if shake_frame > 10:
                shake_frame = 0
            shake_multiplier = settings_window.screen_shake_slider.get_current_value()
            # print(shake_multiplier, math.pow(shake_multiplier, 2))
            # math.pow zodat de waardes worden: 0, 1, 4
            shake_x = random.randint(
                -1 * math.pow(shake_multiplier, 2), 1 * math.pow(shake_multiplier, 2)
            )
            shake_y = random.randint(
                -1 * math.pow(shake_multiplier, 2), 1 * math.pow(shake_multiplier, 2)
            )

        particles, particle_perf = spawn_particles(particle_perf, player, particles)

        if not pause_menu_opened:
            del_list = []

            for i, particle in enumerate(particles):
                particle.update(
                    scrollx + shake_x, scrolly + shake_y, deltaT, player, world
                )
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

        if not pause_menu_opened:
            player.walking(
                keys,
                deltaT,
                pygame.mouse.get_pressed(),
                joystick,
                joystick_input,
                joystick_btn_dict,
                plants,
                dt
            )
            player.update(
                plants,
                keys,
                screen,
                joystick,
                joystick_input,
                player_hp_bar,
                joystick_btn_dict,
                player_bow,
                pygame.mouse.get_pos(),
                scrollx,
                scrolly,
                dt
            )

        if player.hitting or started_shake:
            started_shake = True
            if not started_shake:
                shake_time = time.perf_counter()
            shake(shake_time, scrollx, scrolly)
            shake_frame = 1
            # animals.hit = False

        if not pause_menu_opened:
            particles = enemies.update(
                enemies_spawn,
                player,
                torch_locations_list,
                particles,
                night_count,
                player_bow,
                dt
            )

        main_inventory.draw_holding_items(screen, (scrollx, scrolly))

        if not pause_menu_opened:
            if time.perf_counter() - sky_time > 0.01:
                if not is_night:
                    sky_color = [
                        sky_color[0],
                        sky_color[1],
                        sky_color[2],
                        sky_color[3] + 0.5,
                    ]
                else:
                    sky_color = [
                        sky_color[0],
                        sky_color[1],
                        sky_color[2],
                        sky_color[3] - 0.5,
                    ]

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

        night_count = ui_clock.update(sky_color, is_night, night_count)
        ui_clock.draw(screen)

        scrollx += int((player.x - int((screenWidth - 48) / 2) - scrollx) / 5)
        scrolly += int((player.y - int((screenHeight - 48) / 2) - scrolly) / 5)

        scrollx = max(scrollx, 0)
        scrollx = min(scrollx, 16 * map_w - screenWidth)
        scrolly = max(scrolly, 0)
        scrolly = min(scrolly, 16 * map_h - screenHeight)

        if not pause_menu_opened:
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

        if not pause_menu_opened:
            main_crafting_table.update(
                keys,
                pygame.mouse.get_pos(),
                pygame.mouse.get_pressed(),
                joystick_input,
                joystick,
                (scrollx, scrolly),
                joystick_btn_dict,
            )

    if pause_menu_opened:
        # print("ik ben blij")
        screen.blit(black_surface, (0, 0))

        pause_menu_opened, save_game, quit_game, to_title = pause_menu_window.update(
            events, deltaT
        )
        pause_menu_window.draw()

        if save_game:
            save_world()

        if quit_game:
            playing = False

        if to_title:
            load_save_window.update_game_dirs()
            current_game_state = "TITLE"

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

    # player_bow.update(100, 100, 0)
    # player_bow.draw(screen, scrollx, scrolly)

    fps = clock.get_fps()
    screen.blit(fps_font.render(str(int(fps)), True, (0, 0, 0)), (10, 10))
    pygame.display.update()
    max_fps = settings_window.max_fps_slider.get_current_value()
    deltaT = clock.tick(max_fps)
    dt = deltaT / 16
    # if joystick_input:
    #     if eval(joystick_btn_dict["d-pad-right"]):
    #         print("RIGHT")

pygame.quit()
