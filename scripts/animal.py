import pygame
import time
from func import *
from scripts.ui import HealthBar


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
            "sheep": ["meat ","wool "],
            "sheepbrown": ["meat ","wool "],
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
                    HealthBar((0, 0), (50, 5), 2, hp),  # hp bar 21
                    -1,  # last attack 22
                ]

    def reset_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height

    def draw(self, screen, scrollx, scrolly):
        self.scrollx, self.scrolly = scrollx, scrolly
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
            hp_bar = animal[21]
            last_attack = animal[22]

            if time.perf_counter() - last_attack < 10:
                hp_bar.draw(screen, "black", "darkgray", "red", 2, 2)

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
            hp_bar = animal[21]
            last_attack = animal[22]

            hp_bar.update(
                animal_hp,
                (
                    animal_rect.x - self.scrollx - (animal_rect.w / 2) - 8,
                    animal_rect.y - self.scrolly - 10,
                ),
            )

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
                    hp_bar.damage()
                    animal[22] = time.perf_counter()
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
                    if type(self.drop_item[animal_type]) is list:
                        dropping_item = random.choice(self.drop_item[animal_type])
                    else:
                        dropping_item = self.drop_item[animal_type]
                    self.inventory.dropped_items[len(self.inventory.dropped_items)] = [
                        dropping_item,
                        animal_rect.x + random.choice([-60, 60, 55, -55]),
                        animal_rect.y + random.choice([-60, 60, 55, -55]),
                        time.perf_counter(),
                    ]
                else:
                    for _ in range(random.randint(1, 2)):
                        if type(self.drop_item[animal_type]) is list:
                            dropping_item = random.choice(self.drop_item[animal_type])
                        else:
                            dropping_item = self.drop_item[animal_type]
                        self.inventory.dropped_items[
                            len(self.inventory.dropped_items)
                        ] = [
                            dropping_item,
                            animal_rect.x + random.choice([-60, 60, 55, -55]),
                            animal_rect.y + random.choice([-60, 60, 55, -55]),
                            time.perf_counter(),
                        ]
                for _ in range(30):
                    particles.append(HitParticle(animal[0].x, animal[0].y))

        for delete_animal in sorted(animal_delete_list, reverse=True):
            self.animal_dict.pop(delete_animal)

        return particles
