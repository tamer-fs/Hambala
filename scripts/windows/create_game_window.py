import pygame
import pygame_gui
import os, json, numpy, random
from scripts.uiElements.button_el import Button
from scripts.uiElements.input_entry_el import InputEntry
from func import create_world
from scripts.animal import Animal

pygame.init()
pygame.font.init()

Testfont = pygame.font.SysFont("Calibri", 32)


class CreateGameWindow:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.manager = pygame_gui.UIManager(
            (self.screen_width, self.screen_height),
            theme_path="scripts/windows/title_window.json",
        )
        self.difficulties = ["Easy", "Medium", "Hard"]
        self.difficulty = 0
        # self.test_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text="EXIT BUTTON", manager=self.manager)
        self.btn_h_percent = 7
        self.difficulty_btn = Button(
            (66, "%"),
            (30, "%"),
            (28, "%"),
            (self.btn_h_percent, "%"),
            f"Game Difficulty: {self.difficulties[self.difficulty]}",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.create_game_btn = Button(
            (50, "%"),
            (50, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Create game...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        self.back_btn = Button(
            (15, "%"),
            (92, "%"),
            (25, "%"),
            (self.btn_h_percent, "%"),
            "Back to main menu...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )
        title_rect = pygame.Rect((0, 0), (int(self.screen_width), int(200)))
        self.title = pygame_gui.elements.UILabel(
            manager=self.manager,
            text="CREATE GAME",
            relative_rect=title_rect,
            anchors={"left": "left", "right": "right"},
        )
        self.name_input = InputEntry(
            (34, "%"),
            (30, "%"),
            (28, "%"),
            (self.btn_h_percent, "%"),
            "Game name...",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

        self.seed_input = InputEntry(
            (50, "%"),
            (40, "%"),
            (60, "%"),
            (self.btn_h_percent, "%"),
            "Custom seed... (Optional)",
            self.manager,
            self.screen_width,
            self.screen_height,
        )

    def update_res(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = self.screen.get_size()

        self.manager.set_window_resolution((self.screen_width, self.screen_height))
        self.create_game_btn.update_res(self.screen_width, self.screen_height)
        self.back_btn.update_res(self.screen_width, self.screen_height)
        self.difficulty_btn.update_res(self.screen_width, self.screen_height)
        self.name_input.update_res(self.screen_width, self.screen_height)
        self.seed_input.update_res(self.screen_width, self.screen_height)

        self.seed_input.input_entry.rebuild()
        self.create_game_btn.button.rebuild()
        self.back_btn.button.rebuild()
        self.name_input.input_entry.rebuild()
        self.difficulty_btn.button.rebuild()
        self.title.rebuild()

        self.manager.set_window_resolution((self.screen_width, self.screen_height))

    def update(self, events, mouse_x, mouse_y, mouse_down, loaded_world, delta_time):
        playing = True
        current_game_state = "CREATE"
        self.screen_width, self.screen_height = self.screen.get_size()

        # if events != []:
        #     print(events)
        for event in events:
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_btn.button:
                    current_game_state = "TITLE"
                elif event.ui_element == self.create_game_btn.button:
                    folder_name = self.name_input.input_entry.get_text().replace(
                        " ", ""
                    )
                    folder_name = folder_name.lower()
                    folder_name = folder_name[:50]

                    remove_chars = []
                    for i, char in enumerate(folder_name):
                        if not char in list("abcdefghijklmnopqrstuvwxyz_1234567890"):
                            remove_chars.append(i)

                    folder_name = list(folder_name)
                    for remove_char in reversed(remove_chars):
                        folder_name.pop(remove_char)

                    str_folder_name = ""
                    for char in folder_name:
                        str_folder_name = str_folder_name + char

                    loaded_world = str_folder_name
                    self.can_create = bool(loaded_world)

                    for folder in os.listdir(os.path.join("saves")):
                        if folder == loaded_world:
                            self.can_create = False

                    animal = Animal(
                        random.randint(25, 45), self.screen_width, self.screen_height
                    )

                    if self.can_create:
                        current_game_state = "GAME"
                        save_json = {
                            "game_name": self.name_input.input_entry.get_text(),
                            "game_difficulty": self.difficulty,
                            "time": 0,
                            "night_count": 0,
                            "is_night": False,
                            "animal_dict": animal.return_animal_dict(),
                            "alive_enemies": [],
                            "player": {
                                "x": 1176.0,
                                "y": 1176.0,
                                "energy_value": 100,
                                "food_value": 10000,
                                "health_value": 10,
                                "max_health": 10,
                                "strength": 1,
                                "speed_multiplier": 1,
                                "food_multiplier": 1,
                                "backpack_unlocked": False,
                                "increment_boost": 0,
                            },
                            "inventory": {
                                "block_fill": {
                                    "0": "axe ",
                                    "1": "pickaxe ",
                                    "2": "sword ",
                                    "3": "",
                                    "4": "",
                                    "5": "",
                                    "6": "",
                                    "7": "",
                                    "8": "",
                                    "9": "",
                                    "10": "",
                                    "11": "",
                                    "12": "",
                                    "13": "",
                                    "14": "",
                                    "15": "",
                                    "16": "",
                                    "17": "",
                                    "18": "",
                                    "19": "",
                                    "20": "",
                                    "21": "",
                                    "22": "",
                                    "23": "",
                                    "24": "",
                                    "25": "",
                                    "26": "",
                                },
                                "item_count_dict": {
                                    "0": 1,
                                    "1": 1,
                                    "2": 1,
                                    "3": 0,
                                    "4": 0,
                                    "5": 0,
                                    "6": 0,
                                    "7": 0,
                                    "8": 0,
                                    "9": 0,
                                    "10": 0,
                                    "11": 0,
                                    "12": 0,
                                    "13": 0,
                                    "14": 0,
                                    "15": 0,
                                    "16": 0,
                                    "17": 0,
                                    "18": 0,
                                    "19": 0,
                                    "20": 0,
                                    "21": 0,
                                    "22": 0,
                                    "23": 0,
                                    "24": 0,
                                    "25": 0,
                                    "26": 0,
                                },
                            },
                        }

                        # create folder (os.path.join is professioneel)
                        os.mkdir(os.path.join("saves", str(str_folder_name)))

                        # create save.json
                        with open(
                            os.path.join("saves", str(str_folder_name), "save.json"),
                            "w",
                        ) as f:
                            f.write(json.dumps(save_json))

                        # create world and save world data in txt files
                        map_w, map_h = 150, 150
                        plant_spawn_chance = 3
                        seed = self.seed_input.input_entry.get_text()
                        filtered_seed = ""

                        if seed == "":  # niks ingevuld als seed
                            seed = str(random.randint(0, 100) * random.randint(0, 5))

                        for character in seed:
                            if character.isdigit():
                                filtered_seed = filtered_seed + str(character)
                            else:
                                filtered_seed = filtered_seed + str(ord(character))
                        print(filtered_seed)
                        filtered_seed = int(filtered_seed)

                        plants, world, world_rotation = create_world(
                            map_w,
                            map_h,
                            plant_spawn_chance,
                            filtered_seed,
                        )

                        with open(
                            os.path.join("saves", str(str_folder_name), "world.txt"),
                            "w",
                        ) as f:
                            numpy.savetxt(f, world.astype(int), fmt="%i")

                        with open(
                            os.path.join(
                                "saves", str(str_folder_name), "world_rotation.txt"
                            ),
                            "w",
                        ) as f:
                            numpy.savetxt(f, world_rotation.astype(int), fmt="%i")

                        with open(
                            os.path.join("saves", str(str_folder_name), "plants.txt"),
                            "w",
                        ) as f:
                            numpy.savetxt(f, plants.astype(int), fmt="%i")

                        with open("last_played.txt", "w") as f:
                            f.write(str_folder_name)

                        # import pdb

                        # pdb.set_trace()

                elif event.ui_element == self.difficulty_btn.button:
                    self.difficulty += 1
                    if self.difficulty > 2:
                        self.difficulty = 0
                    self.difficulty_btn.button.set_text(
                        f"Game Difficulty: {self.difficulties[self.difficulty]}"
                    )
            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution(
                    (self.screen_width, self.screen_height)
                )
                self.create_game_btn.update_res(self.screen_width, self.screen_height)
                self.back_btn.update_res(self.screen_width, self.screen_height)
                self.difficulty_btn.update_res(self.screen_width, self.screen_height)
                self.name_input.update_res(self.screen_width, self.screen_height)
                self.seed_input.update_res(self.screen_width, self.screen_height)

                self.seed_input.input_entry.rebuild()
                self.create_game_btn.button.rebuild()
                self.back_btn.button.rebuild()
                self.name_input.input_entry.rebuild()
                self.difficulty_btn.button.rebuild()
                self.title.rebuild()

            self.manager.process_events(event)

        self.manager.update(delta_time)

        return playing, current_game_state, loaded_world

    def draw(self):
        self.manager.draw_ui(self.screen)
